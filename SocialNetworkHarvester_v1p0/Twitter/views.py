from django.shortcuts import *
import json
from django.db.models import Count
from django.contrib.auth.models import User
from .models import TWUser, Tweet, Hashtag
from datetime import datetime
import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0

def twitterBaseView(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    })
    return render_to_response('Twitter/TwitterBase.html', context)

def twUserView(request, TWUser_value):

    if TWUser.objects.filter(screen_name=TWUser_value):
        twUser = TWUser.objects.get(screen_name=TWUser_value)
    elif TWUser.objects.filter(_ident=TWUser_value):
        twUser = TWUser.objects.get(_ident=TWUser_value)
    elif TWUser.objects.filter(pk=TWUser_value):
        twUser = TWUser.objects.get(pk=TWUser_value)
    else:
        return Http404('No TWUser matches that value')
    log('twUser: %s'%twUser)
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
    context = RequestContext(request, {
        'user': request.user,
        'hashtag_term':TWHashtagTerm,
    })
    return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    context = RequestContext(request, {
        'user': request.user,
        'tweet_id': tweetId,
    })
    return render_to_response('Twitter/TwitterTweet.html', context)

@viewsLogger.debug()
def ajaxTWUserTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = TWUser.objects.all()
    else:
        queryset = aspiraUser.userProfile.twitterUsersToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    return HttpResponse(json.dumps(response), content_type='application/json')


@viewsLogger.debug()
def ajaxTWHashtagTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = Hashtag.objects.all()
    else:
        queryset = aspiraUser.userProfile.twitterHashtagsToHarvest.all()
    response = generateAjaxTableResponse(queryset, request)
    return HttpResponse(json.dumps(response), content_type='application/json')


@viewsLogger.debug()
def ajaxTWTweetTable(request):
    try:
        queryset = Tweet.objects.none()
        for source in request.GET['sources'].split(','):
            if source != "":
                val = re.match(r'^(?P<type>[^0-9]*)_(?P<id>[0-9]*)',source)
                id = val.group('id')
                type = val.group('type')
                if type in ["TWUser", "Hashtag"]:
                    className = globals()[type]
                    item = get_object_or_404(className, pk=id)
                    queryset = queryset | item.tweets.all()
        response = generateAjaxTableResponse(queryset, request)
        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        viewsLogger.exception("Error occured in ajaxTWTweetTable:")
        return HttpResponse(json.dumps({"error":"An error occured in views"}))

def getAttrsJson(obj, attrs):
    l = {}
    for attr in attrs:
        value = getattr(obj,attr)
        if isinstance(value, TWUser):
            value = value.screen_name
        if isinstance(value, datetime):
            value =  datetime.strftime(value, '%a %b %d %H:%M:%S %z %Y')
        l[attr] = value
    l['DT_RowId'] = "%s_%s"%(type(obj).__name__, obj.id)
    return l

@viewsLogger.debug(showArgs=True)
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
    if order == 'desc':
        field = '-'+field
    log('ordering by %s'%field)
    return queryset.order_by(field)

def filterQuerySet(queryset, fields, term):
    filteredQueryset = queryset.filter(id=-1)
    for field in fields:
        if queryset.model._meta.get_field(field) == Tweet.user.field:
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__screen_name__contains":'%s'%term})
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__name__contains":'%s'%term})
        else:
            filteredQueryset = filteredQueryset | queryset.filter(**{field+"__contains":'%s'%term})
    return filteredQueryset

'''
EXAMPLE OF PARAMS EXPECTED IN generateAjaxTableResponse(): https://datatables.net/manual/server-side

'_': '1457036532442',
 'bRegex': 'false',
 'bRegex_0': 'false',
 'bRegex_1': 'false',
 'bRegex_2': 'false',
 'bRegex_3': 'false',
 'bRegex_4': 'false',
 'bRegex_5': 'false',
 'bRegex_6': 'false',
 'bSearchable_0': 'false',
 'bSearchable_1': 'true',
 'bSearchable_2': 'true',
 'bSearchable_3': 'false',
 'bSearchable_4': 'false',
 'bSearchable_5': 'false',
 'bSearchable_6': 'true',
 'bSortable_0': 'false',
 'bSortable_1': 'true',
 'bSortable_2': 'true',
 'bSortable_3': 'true',
 'bSortable_4': 'true',
 'bSortable_5': 'true',
 'bSortable_6': 'true',
 'fields': 'name,screen_name,followers_count,friends_count,statuses_count,location',
 'iColumns': '7',
 'iDisplayLength': '10',
 'iDisplayStart': '0',
 'iSortCol_0': '3',
 'iSortingCols': '1',
 'mDataProp_0': '0',
 'mDataProp_1': '1',
 'mDataProp_2': '2',
 'mDataProp_3': '3',
 'mDataProp_4': '4',
 'mDataProp_5': '5',
 'mDataProp_6': '6',
 'sColumns': ',,,,,,',
 'sEcho': '3',
 'sSearch': 'harper',
 'sSearch_0': '',
 'sSearch_1': '',
 'sSearch_2': '',
 'sSearch_3': '',
 'sSearch_4': '',
 'sSearch_5': '',
 'sSearch_6': '',
 'sSortDir_0': 'asc'}
'''