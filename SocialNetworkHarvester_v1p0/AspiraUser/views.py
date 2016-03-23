from django.shortcuts import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Twitter.models import TWUser, Tweet, Hashtag, follower
from django.db.models import Count, Max

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0


def lastUrlOrHome(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    if request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect('/')

@login_required()
def userDashboard(request):
    aspiraUser = request.user.userProfile
    twitterUserLimit = aspiraUser.twitterUsersToHarvestLimit
    twitterHashtagLimit = aspiraUser.twitterHashtagToHarvestLimit
    collectedTweets = Tweet.objects.filter(user__harvested_by=aspiraUser).count() # TODO: Add hashtags tweets count
    mostActiveTwitterUser = aspiraUser.twitterUsersToHarvest.annotate(harvested_count=Count('tweets')).order_by("-harvested_count")[0]
    twitterUserPercent = 0
    if twitterUserLimit > 0:
        twitterUserPercent = aspiraUser.twitterUsersToHarvest.count()*100/twitterUserLimit
    twitterHashtagPercent = 0
    if twitterHashtagLimit > 0:
        twitterHashtagPercent = aspiraUser.twitterHashtagsToHarvest.count()*100/twitterHashtagLimit
    mostActiveHashtag = "#FooBar"
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Dashboard", "/"),
        ],
        "twitterUserLimit": twitterUserLimit if twitterUserLimit>0  else "inf",
        "twitterHashtagLimit":twitterHashtagLimit if twitterHashtagLimit>0  else "inf",
        "twitterUserUsage": aspiraUser.twitterUsersToHarvest.count(),
        "twitterUserPercent":twitterUserPercent,
        "twitterHashtagPercent":twitterHashtagLimit,
        "twitterHashtagUsage": aspiraUser.twitterHashtagsToHarvest.count(),
        "collectedTweets": collectedTweets,
        "mostActiveTwitterUser": mostActiveTwitterUser,
        "mostActiveHashtag":mostActiveHashtag,
    })
    return render_to_response('AspiraUser/dashboard.html', context)


def userLogin(request):
    username = request.POST['username']
    pw = request.POST['password']
    user = authenticate(username=username, password=pw)
    if user is not None:
        login(request, user)

    return lastUrlOrHome(request)

def userLoginPage(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('AspiraUser/login_page.html', context)


def userLogout(request):
    logout(request)
    return lastUrlOrHome(request)

@login_required()
def userSettings(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Settings", "/settings"),
        ]
    })
    return render_to_response('AspiraUser/settings.html', context)

@login_required()
def editUserSettings(request):
    user = request.user
    for atr in request.POST:
        log("%s: %s"%(atr, request.POST[atr]))
        if atr[0] == 'u':
            setattr(user, atr[2:], request.POST[atr])
        elif atr[0] == 'p':
            setattr(user.userProfile, atr[2:], request.POST[atr])
    user.save()
    user.userProfile.save()

    return userSettings(request)