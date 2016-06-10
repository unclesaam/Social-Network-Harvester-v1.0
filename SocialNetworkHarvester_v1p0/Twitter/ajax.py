from django.shortcuts import *
import json
from django.db.models import Count
from django.contrib.auth.models import User
from .models import TWUser, Tweet, Hashtag, follower, HashtagHarvester
from datetime import datetime
import re
from django.contrib.auth.decorators import login_required
from AspiraUser.views import getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


@login_required()
def ajaxTWUserTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = TWUser.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterUsersToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required()
def ajaxTWHashtagTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = HashtagHarvester.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterHashtagsToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    # log(response)
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required()
#@viewsLogger.debug(showArgs=True)
def ajaxTWTweetTable(request):
    try:
        queryset = Tweet.objects.none()
        excludeRetweets = False
        if 'exclude_retweets' in request.GET and request.GET['exclude_retweets'] == 'true':
            excludeRetweets = True
        for source in request.GET['selected_rows'].split(','):
            if source != "":
                val = re.match(r'^(?P<type>[^0-9]*)_(?P<id>[0-9]*)', source)
                id = val.group('id')
                type = val.group('type')
                # log("type: %s"%type)
                if type == "TWUser":
                    className = globals()[type]
                    item = get_object_or_404(className, pk=id)
                    queryset = queryset | item.tweets.all()
                elif type == "HashtagHarvester":
                    className = globals()[type]
                    item = get_object_or_404(className, pk=id)
                    queryset = queryset | item.hashtag.tweets.all()
                elif type == "Hashtag":
                    className = globals()[type]
                    item = get_object_or_404(className, pk=id)
                    queryset = queryset | item.tweets.all()
                if excludeRetweets:
                    queryset = queryset.filter(retweet_of__isnull=True)
        # log(queryset)
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWTweetTable:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def ajaxTWUserMentions(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.mentions.filter(retweet_of__isnull=True)
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def ajaxTWFollowersTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.followers.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


def ajaxTWFriendsTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.friends.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def ajaxTWFavoritesTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.favorite_tweets.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def ajaxTWRetweets(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.retweets.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWRetweets:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def TWMentionnedUsers(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.user_mentions.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def TWFavoritedBy(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.favorited_by.filter(ended__isnull=True) # gives a favorited_by query
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


@login_required()
def TWContainedHashtags(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.hashtags.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return HttpResponse(json.dumps({"error": "An error occured in views"}))


#@viewsLogger.debug(showArgs=True)
def getAttrsJson(obj, attrs):
    l = {}
    for attr in attrs:
        if attr == '': break
        subAttrs = attr.split('__')
        value = getattr(obj, subAttrs[0])
        if callable(value):
            value = value()
        # log("%s: %s"%(subAttrs[0], value))
        if len(subAttrs) > 1:
            for subAttr in subAttrs[1:]:
                value = getattr(value, subAttr)
                if callable(value):
                    value = value()
                    # log("%s: %s"%(subAttr, value))
        if isinstance(value, TWUser):
            value = value.screen_name
        if isinstance(value, datetime):
            #value = datetime.strftime(value, '%b %d %Y %H:%M')
            value = datetime.strftime(value, '%b %d %Y')
        if '_ident' in attr:  # javascript doesn't understand big integers and truncates the last two bits to 00
            l[attr] = str(value)
        else:
            l[attr] = value
    l['DT_RowId'] = "%s_%s" % (type(obj).__name__, obj.id)
    return l

#@viewsLogger.debug(showArgs=True)
def generateAjaxTableResponse(queryset, request):
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

    response["data"] = [getAttrsJson(item, fields) for item in queryset.iterator()]
    #pretty(response)
    return response

#@viewsLogger.debug(showArgs=True)
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
