from django.shortcuts import *
import json
from django.db.models import Count
from django.contrib.auth.models import User
from .models import TWUser, Tweet, Hashtag, follower
from datetime import datetime
import re
from django.contrib.auth.decorators import login_required


from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0

@login_required()
def twitterBaseView(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    })
    return render_to_response('Twitter/TwitterBase.html', context)

def twUserView(request, TWUser_value):

    twUser = TWUser.objects.filter(screen_name=TWUser_value)
    if not twUser:
        try:
            twUser = TWUser.objects.filter(_ident=TWUser_value)
        except:
            pass
    if not twUser:
        try:
            twUser = TWUser.objects.filter(pk=TWUser_value)
        except:
            pass
    if not twUser:
        raise Http404('No TWUser matches that value')
    twUser = twUser[0]
    context = RequestContext(request, {
        'user': request.user,
        'twUser':twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/"+TWUser_value),
        ],
    })
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        return render_to_response('Twitter/TwitterUserSnip.html', context)
    else:
        return render_to_response('Twitter/TwitterUser.html', context)

def twHashtagView(request, TWHashtagTerm):
    hashtag = get_object_or_404(Hashtag, term=TWHashtagTerm)
    context = RequestContext(request, {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(hashtag), "#"),
        ],
    })
    return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    context = RequestContext(request, {
        'user': request.user,
        'tweet_id': tweetId,
        'navigator': [
            ("Twitter", "/twitter"),
            (tweetId, "/twitter/tweet/"+tweetId),
        ],
    })
    return render_to_response('Twitter/TwitterTweet.html', context)

def ajaxTWUserTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = TWUser.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterUsersToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def ajaxTWHashtagTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = Hashtag.objects.all()
    else:
        queryset = aspiraUser.userProfile.twitterHashtagsToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def ajaxTWTweetTable(request):
    try:
        queryset = Tweet.objects.none()
        excludeRetweets = False
        if 'exclude_retweets' in request.GET and request.GET['exclude_retweets'] == 'true':
            excludeRetweets = True
        for source in request.GET['selected_rows'].split(','):
            if source != "":
                val = re.match(r'^(?P<type>[^0-9]*)_(?P<id>[0-9]*)',source)
                id = val.group('id')
                type = val.group('type')
                if type in ["TWUser", "Hashtag"]:
                    className = globals()[type]
                    item = get_object_or_404(className, pk=id)
                    if excludeRetweets:
                        queryset = queryset | item.tweets.filter(retweet_of__isnull=excludeRetweets)
                    else:
                        queryset = queryset | item.tweets.all()
                    log(queryset)
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWTweetTable:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def ajaxTWUserMentions(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.mentions.filter(retweet_of__isnull=True)
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def ajaxTWFollowersTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.followers.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def ajaxTWFriendsTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.friends.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def ajaxTWFavoritesTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.favorite_tweets.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def getAttrsJson(obj, attrs):
    l = {}
    for attr in attrs:
        subAttrs = attr.split('__')
        value = getattr(obj,subAttrs[0])
        if callable(value):
            value = value()
        #log("%s: %s"%(subAttrs[0], value))
        if len(subAttrs) > 1:
            for subAttr in subAttrs[1:]:
                value = getattr(value,subAttr)
                #log("%s: %s"%(subAttr, value))
        if isinstance(value, TWUser):
            value = value.screen_name
        if isinstance(value, datetime):
            value =  datetime.strftime(value, '%a %b %d %H:%M:%S %z %Y')
        l[attr] = value
    l['DT_RowId'] = "%s_%s"%(type(obj).__name__, obj.id)
    return l

def generateAjaxTableResponse(queryset, request):
    params = request.GET
    response = {
                "recordsTotal" : queryset.count(),
                "recordsFiltered" : queryset.count(),
                'fullURL' : request.get_full_path(),
                }
    fields = []
    if 'fields' in params:
        fields = params['fields'].split(',')

        if "iSortCol_0" in params:
            ordering_column = int(params['iSortCol_0'])-1
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
            queryset = queryset[start:start+length]

    response["data"] = [getAttrsJson(item, fields) for item in queryset.iterator()]
    return response

def orderQuerySet(queryset, field, order):
    orderingBy = field
    if order == 'desc':
        orderingBy = '-'+orderingBy
    ret = queryset.order_by(orderingBy).exclude(**{field+"__isnull":True})
    try:
        ret = ret.exclude(**{field:""})
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
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__screen_name__contains":'%s'%term})
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__name__contains":'%s'%term})
        else:
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__icontains":'%s'%term})
    return filteredQueryset
