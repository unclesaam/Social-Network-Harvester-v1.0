from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS
from AspiraUser.models import getUserSelection, resetUserSelection, FBAccessToken
import re
from Facebook.models import *
from Facebook.fbClient import FBClient
import facebook
from tool.views.tables import readLinesFromCSV

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
    limit = request.user.userProfile.facebookPagesToHarvestLimit
    currentCount = request.user.userProfile.facebookPagesToHarvest.count()
    if limit <= currentCount:
        return jResponse({
            'status': 'exception',
            'errors': ["Vous avez atteint votre limite de pages à collecter."],
        })

    pageUrls = [url for url in request.POST.getlist('pageUrl') if url != ""]
    invalids = []
    if 'Browse' in request.FILES:
        fileUrls, errors = readLinesFromCSV(request)
        pageUrls += fileUrls
        invalids += errors
    if limit <= currentCount + len(pageUrls):
        pageUrls = pageUrls[:limit-currentCount]
    try:
        invalids += addFbPages(request, pageUrls)
    except FacebookAccessTokenException:
        return jResponse({
            'status': 'exception',
            'errors': ["Vous devez d'abord vous connecter à Facebook à l'aide d'un compte.",
                       "Veuillez vous connecter via votre page de <a class='classic' href='/user/settings'>paramètres</a>"],
        })
    numAddedPages = len(pageUrls) - len(invalids)
    if not numAddedPages:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas un URL valide' % url for url in invalids],
        })
    return jResponse({
        'status': 'ok',
        'messages': [
            '%s pages publiques %s ont été ajoutées à votre liste (%i erreur%s)' % (numAddedPages, plurial(numAddedPages),
                                                                            len(invalids), plurial(len(invalids)))]
    })

#@viewsLogger.debug(showArgs=True)
def addFbPages(request, pageUrls):
    aspiraProfile = request.user.userProfile
    if not hasattr(aspiraProfile,"fbAccessToken"): raise FacebookAccessTokenNotSetException()
    if aspiraProfile.fbAccessToken.is_expired(): raise FacebookAccessTokenExpiredException()
    graph = facebook.GraphAPI(aspiraProfile.fbAccessToken._token)
    invalids = []
    response = None
    try:
        response = graph.get_objects(pageUrls)
    except Exception as e:
        pretty(response)
        return pageUrls
    for url in response.keys():
        if 'name' in response[url] and 'id' in response[url]:
            jUser = graph.get_object(response[url]['id'], fields='name,id')
            fbPage, new = FBPage.objects.get_or_create(_ident=response[url]['id'])
            if new:
                fbProfile, new = FBProfile.objects.get_or_create(_ident=fbPage._ident)
                if new:
                    fbProfile.type = 'P'
                    fbProfile.fbPage = fbPage
                    fbProfile.save()
            fbPage.name = response[url]['name']
            fbPage.save()
            aspiraProfile.facebookPagesToHarvest.add(fbPage)
            aspiraProfile.save()
        else:
            invalids.append(response[url]['id'])
    return invalids


class FacebookAccessTokenException(Exception):pass
class FacebookAccessTokenNotSetException(FacebookAccessTokenException):pass
class FacebookAccessTokenExpiredException(FacebookAccessTokenException):pass



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
    profile.facebookApp_parameters_error = False
    profile.save()
    return HttpResponse("ok")

