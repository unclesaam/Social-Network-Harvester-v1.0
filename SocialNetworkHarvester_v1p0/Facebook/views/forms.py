from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS
from AspiraUser.models import getUserSelection, resetUserSelection, FBAccessToken
import re
from Facebook.models import *
from Facebook.fbClient import FBClient
import facebook

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG

log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

plurial = lambda i: 's' if int(i) > 1 else ''

validFormNames = [
    'FBAddUser',
    'setFacebookToken'
]

@login_required()
def formBase(request, formName):
    if not request.user.is_authenticated(): return jsonUnauthorizedError(request)
    if not formName in validFormNames: return jsonBadRequest(request, 'Specified form does not exists')
    try:
        return globals()[formName](request)
    except:
        viewsLogger.exception("ERROR OCCURED IN %s AJAX WITH FORM NAME '%s':" % (__name__,formName))
        return jsonUnknownError(request)


@viewsLogger.debug()
def FBAddUser(request):
    if not 'userUrl' in request.POST and not 'Browse' in request.FILES: return jsonBadRequest(request,
                                                                                                 'No channel url specified')
    userUrls = request.POST.getlist('userUrl')
    '''if 'Browse' in request.FILES:
        userUrls += readLinesFromCSV(request)'''
    invalids = addUsers(request, userUrls)

    numAddedUsers = len(userUrls) - len(invalids)
    if not numAddedUsers:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas un URL valide' % url for url in invalids],
        })
    return jResponse({
        'status': 'ok',
        'messages': [
            '%s utilisateurs %s ont été ajoutées à votre liste (%i erreurs%s)' % (numAddedUsers, plurial(numAddedUsers),
                                                                            len(invalids), plurial(len(invalids)))]
    })


#@viewsLogger.debug()
def addUsers(request, userUrls):
    profile = request.user.userProfile
    if not hasattr(profile,"fbAccessToken"): raise FacebookAccessTokenNotSetException()
    if profile.fbAccessToken.is_expired(): raise FacebookAccessTokenExpiredException()
    graph = facebook.GraphAPI(profile.fbAccessToken._token)
    invalids = []
    response = graph.get_objects(list(filter(None, userUrls)), fields=['id', 'og_object.fields(["id"])'])
    pretty(response)
    for key in response.keys():
        if 'og_object' in response[key]:
            pretty(graph.get_object(response[key]['og_object']['id']))
    '''
    newChannel = None
    match = re.match(r'https?://www.facebook.com/(?P<item1>[\w\.]+)?/?(?P<item2>[\w\.]+)?/?.*', url)
    if match and match.group('item1'):
        urlId = match.group('item2') or match.group('item1')
        nodeType = match.group('item1') if match.group('item2') else None
        response = graph.get_object(url)
        log(response)
        #newUser, new = FBUser.objects.get_or_create(userName=match.group('username'))
    '''
    return invalids

class FacebookAccessTokenNotSetException(Exception):pass
class FacebookAccessTokenExpiredException(Exception):pass

def setFacebookToken(request):
    if not 'fbToken' in request.POST: return jsonBadRequest(request, "'fbToken' is required")
    profile = request.user.userProfile
    if not hasattr( profile, 'fbAccessToken') :
        profile.fbAccessToken = FBAccessToken.objects.create()
        profile.save()
    fbAccessToken = profile.fbAccessToken
    fbAccessToken._token = request.POST['fbToken']
    if not request.POST['fbToken']:
        fbAccessToken.expires = None;
    else:
        fbAccessToken.extend()
    fbAccessToken.save()
    return HttpResponse("ok")

