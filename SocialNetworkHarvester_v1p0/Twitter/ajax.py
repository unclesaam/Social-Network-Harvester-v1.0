from django.shortcuts import *
import json
from django.http import StreamingHttpResponse
from django.db.models import Count
from django.contrib.auth.models import User
from .models import TWUser, Tweet, Hashtag, follower, HashtagHarvester
from datetime import datetime
import re
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


######### MAIN PAGE #######
@login_required()
def ajaxTWUserTable(request, aspiraUserId):
    aspiraUser = request.user
    if aspiraUser.is_staff:
        queryset = TWUser.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterUsersToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("TWUser", 'TWUserTable')
    return ajaxResponse(queryset, request, selecteds)

@login_required()
def ajaxTWHashtagTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = HashtagHarvester.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterHashtagsToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("Hashtag", 'TWHashtagTable')
    return ajaxResponse(queryset, request, selecteds)

@login_required()
def ajaxTWTweetTable(request):
    try:
        #queryset = Tweet.objects.none()
        userSelection = getUserSelection(request)
        selectedTWUsers = userSelection.getSavedQueryset('TWUser', 'TWUserTable')
        selectedHashHarvesters = userSelection.getSavedQueryset('HashtagHarvester', 'TWHashtagTable')
        queryset = userSelection.getSavedQueryset('Tweet', 'TWTweetTable')
        options = userSelection.getQueryOptions('TWTweetTable')
        for user in selectedTWUsers.all():
            queryset = queryset | user.tweets.all()
        for hashtagHarvester in selectedHashHarvesters.all():
            queryset = queryset | hashtagHarvester.hashtag.tweets.all()
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        selecteds = userSelection.getSavedQueryset("Tweet", 'TWTweetTable')
        return ajaxResponse(queryset.distinct(), request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWTweetTable:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


####### TWUSER PAGE ########
@login_required()
def ajaxTWUserTweetTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWUserTweetTable')
        options = tableRowsSelections.getQueryOptions('TWUserTweetTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def ajaxTWUserMentions(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.mentions.filter(retweet_of__isnull=True)
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWUserMentionsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def ajaxTWFollowersTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.followers.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("follower", 'TWFollowersTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def ajaxTWFriendsTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.friends.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("follower", 'TWFriendsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def ajaxTWFavoritesTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.favorite_tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("favorite_tweet", 'TWUserFavoritesTable')
        options = tableRowsSelections.getQueryOptions('TWUserFavoritesTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


####### TWEET PAGE #######
@login_required()
def ajaxTWRetweets(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.retweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWRetweetTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWRetweets:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def TWMentionnedUsers(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.user_mentions.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("TWUser", 'TWMentionnedUsersTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def TWFavoritedBy(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.favorited_by.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("favorite_tweet", 'TWFavoritedByTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def TWContainedHashtags(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.hashtags.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Hashtag", 'TWContainedHashtagsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))

@login_required()
def TWHashtagTweetTable(request, HashtagId):
    try:
        hashag = get_object_or_404(Hashtag, pk=HashtagId)
        queryset = hashag.tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'HashtagTweetTable')
        options = tableRowsSelections.getQueryOptions('HashtagTweetTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def TWRepliesTable(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.replied_by.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWTweetRepliesTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


####################### UTILS #######################

def ajaxResponse(queryset, request, selecteds):
    selecteds = selecteds.distinct()
    if 'download' in request.GET and request.GET['download'] == 'true':
        if request.GET['fileType'] == 'csv':
            return generateCSVDownload(request, selecteds)
        elif request.GET['fileType'] == 'json':
            return generateJSONDownload(request, selecteds)
    else:
        response = generateAjaxTableResponse(queryset, request, selecteds)
        return HttpResponse(json.dumps(response), content_type='application/json')

def generateAjaxTableResponse(queryset, request, selecteds):
    params = request.GET
    response = {
        "recordsTotal": queryset.count(),
        "recordsFiltered": queryset.count(),
        'fullURL': request.get_full_path(),
    }
    fields = []
    if 'fields' in params:
        fields = params['fields'].split(',')
        if "iSortCol_0" in params:
            ordering_column = int(params['iSortCol_0']) - 1
            if ordering_column >= 0:
                queryset = orderQuerySet(queryset, fields[ordering_column], params['sSortDir_0'])

        if 'sSearch' in params and params['sSearch'] != '':
            searchables_keys = [value for key, value in sorted(params.items()) if key.startswith("bSearchable_")][1:]
            searchable_fields = [pair[0] for pair in zip(fields, searchables_keys) if pair[1] == 'true']
            queryset = filterQuerySet(queryset, searchable_fields, params['sSearch'])
            response['recordsFiltered'] = queryset.count()

        if "iDisplayStart" in params and "iDisplayLength" in params:
            start = int(params['iDisplayStart'])
            length = int(params['iDisplayLength'])
            queryset = queryset[start:start + length]

    response["data"] = [getValuesAsJson(item, fields) for item in queryset.iterator()]
    response['selecteds'] = [item.get_obj_ident() for item in queryset if item in selecteds]
    response['selectedCount'] = selecteds.count()
    return response

def orderQuerySet(queryset, field, order):
    orderingBy = field
    if order == 'desc':
        orderingBy = '-' + orderingBy
    ret = queryset.order_by(orderingBy).exclude(**{field + "__isnull": True})
    try:
        ret = ret.exclude(**{field: ""})
    except:
        pass
    return ret

def filterQuerySet(queryset, fields, term):
    filteredQueryset = queryset.filter(id=-1)
    for field in fields:
        subFields = field.split('__')
        type = queryset.model._meta.get_field(subFields[0])
        if len(subFields) > 1:
            type = type.rel.to
            for subfield in subFields[1:]:
                type = type._meta.get_field(subfield)
        if type == Tweet.user.field:
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__screen_name__contains": '%s' % term})
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__name__contains": '%s' % term})
        else:
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__icontains": '%s' % term})
    return filteredQueryset

def getValuesAsJson(obj, attrs):
    l = {}
    for attr in attrs:
        if attr == '': break
        subAttrs = attr.split('__')
        value = getattr(obj, subAttrs[0])
        if hasattr(value, 'all'):
            value = value.all()
        elif callable(value):
            value = value()
        # log("%s: %s"%(subAttrs[0], value))
        if len(subAttrs) > 1:
            for subAttr in subAttrs[1:]:
                value = getattr(value, subAttr)
                if hasattr(value, 'all'):
                    value = value.all()
                elif callable(value):
                    value = value()
                    # log("%s: %s"%(subAttr, value))
        if isinstance(value, TWUser):
            value = value.screen_name
        if isinstance(value, datetime):
            # value = datetime.strftime(value, '%b %d %Y %H:%M')
            value = datetime.strftime(value, '%b %d %Y')
        if '_ident' in attr:
            l[attr] = "_%s" % value
        else:
            l[attr] = value
    l['DT_RowId'] = obj.get_obj_ident()
    return l


# @viewsLogger.debug(showArgs=True)
def getValuesAsList(obj, fields):
    json = getValuesAsJson(obj, fields)
    ret = []
    for field in fields:
        ret.append(json[field])
    return ret


#@viewsLogger.debug(showArgs=True)
def getColumnsDescriptions(model, fields, infoType):
    columns = []
    fieldsDescription = model.get_fields_description()
    for field in fields:
        if '__' not in field:
            columns.append(fieldsDescription[field][infoType])
        else:
            subfields = field.split('__')
            submodel = getattr(model, subfields[0])
            for subfield in subfields[1:-1]:
                submodel = getattr(submodel, subfield)
            fieldsDescription = submodel.get_fields_description()
            columns.append(fieldsDescription[subfields[-1]][infoType])
    return columns


################### TABLE STREAMS ###################
import io, csv, types

#@viewsLogger.debug(showArgs=True)
def generateCSVDownload(request, queryset):
    def dataStream():
        csvfile = io.StringIO()
        csvfile.write('\ufeff')  # Byte-Order-Mark to insure UTF8
        csvwriter = csv.writer(csvfile)
        fields = request.GET['fields'].split(',')
        temp = queryset.model.objects.all()[0]
        csvwriter.writerow(getColumnsDescriptions(temp, fields, 'name'))
        csvwriter.writerow(getColumnsDescriptions(temp, fields, 'description'))
        if not queryset:
            csvfile.seek(0)
            yield csvfile.read()
        for obj in queryset.iterator():
            csvwriter.writerow(getValuesAsList(obj, fields))
            csvfile.seek(0)
            data = csvfile.read()
            csvfile.seek(0)
            csvfile.truncate()
            yield data

    response = StreamingHttpResponse(dataStream(), content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=%s" % request.GET['filename'] + '.csv'
    return response

#@viewsLogger.debug(showArgs=True)
def generateJSONDownload(request, selecteds):
    return HttpResponse('Work in progess')
