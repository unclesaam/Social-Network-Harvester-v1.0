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
    'FBAddPage',
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


#@viewsLogger.debug()
def FBAddPage(request):
    if not 'pageUrl' in request.POST and not 'Browse' in request.FILES: return jsonBadRequest(request,
                                                                                                 'No page url specified')
    if request.user.userProfile.facebookPagesToHarvestLimit \
            <= request.user.userProfile.facebookPagesToHarvest.count():
        return jResponse({
            'status': 'exception',
            'errors': ["Vous avez atteint la limite de pages à collecter permise."],
        })

    pageUrls = request.POST.getlist('pageUrl')
    pageUrls = list(filter(None, pageUrls))
    invalids = addFbPages(request, pageUrls)

    numAddedPages = len(pageUrls) - len(invalids)
    if not numAddedPages:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas un URL valide' % url for url in invalids],
        })
    return jResponse({
        'status': 'ok',
        'messages': [
            '%s pages publiques %s ont été ajoutées à votre liste (%i erreurs%s)' % (numAddedPages, plurial(numAddedPages),
                                                                            len(invalids), plurial(len(invalids)))]
    })


@viewsLogger.debug()
def addFbPages(request, userUrls):
    aspiraProfile = request.user.userProfile
    if not hasattr(aspiraProfile,"fbAccessToken"): raise FacebookAccessTokenNotSetException()
    if aspiraProfile.fbAccessToken.is_expired(): raise FacebookAccessTokenExpiredException()
    graph = facebook.GraphAPI(aspiraProfile.fbAccessToken._token)
    invalids = []
    response = graph.get_objects(userUrls)
    #pretty(response)
    for url in response.keys():
        if 'name' in response[url] and 'id' in response[url]:
            jUser = graph.get_object(response[url]['id'], fields='name,id')
            fbPage, new = FBPage.objects.get_or_create(_ident=response[url]['id'])
            if new:
                FBProfile.objects.create(type='P', fbPage=fbPage, _ident=fbPage._ident)
            fbPage.name = response[url]['name']
            fbPage.save()
            aspiraProfile.facebookPagesToHarvest.add(fbPage)
            aspiraProfile.save()
        else:
            invalids.append(response[url]['id'])
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

