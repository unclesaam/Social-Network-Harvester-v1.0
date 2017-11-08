from django.contrib.auth.decorators import login_required
from AspiraUser.models import UserProfile, getUserSelection, resetUserSelection
from django.db.models import Count
from django.shortcuts import render, HttpResponseRedirect
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.utils.timezone import utc



from Twitter.models import *
from Youtube.models import *
from Facebook.models import *
from tool.views.ajaxTables import digestQuery, cleanQuery





from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0




def lastUrlOrHome(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    if request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect('/')

def addMessagesToContext(request, context):
    if 'aspiraErrors' in request.session:
        context['aspiraErrors'] = request.session['aspiraErrors']
    if 'aspiraMessages' in request.session:
        context['aspiraMessages'] = request.session['aspiraMessages']
    request.session['aspiraMessages'] = []
    request.session['aspiraErrors'] = []
    return request, context


@login_required()
def userDashboard(request):
    resetUserSelection(request)
    aspiraUser = request.user.userProfile
    context = {
        'user': request.user,
        "navigator": [
            ("Tableau de bord", "/"),
        ],
        "twStats": getTwitterStats(aspiraUser),
        "ytStats": getYoutubeStats(aspiraUser),
        "fbStats": getFacebookStats(aspiraUser),
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/dashboard.html', context)


def getTwitterStats(aspiraUser):
    twitterUserLimit = aspiraUser.twitterUsersToHarvestLimit
    twitterHashtagLimit = aspiraUser.twitterHashtagsToHarvestLimit
    collectedTweets = Tweet.objects.filter(user__harvested_by=aspiraUser).count() + \
                      Tweet.objects.filter(harvested_by__harvested_by=aspiraUser).count()
    mostActiveTwitterUser = "None"
    twitterUserUsage = aspiraUser.twitterUsersToHarvest.count()
    if twitterUserUsage > 0:
        mostActiveTwitterUser = \
            aspiraUser.twitterUsersToHarvest.annotate(harvested_count=Count('tweets')).order_by("-harvested_count")[0]
    twitterUserPercent = 0
    if twitterUserLimit > 0:
        twitterUserPercent = twitterUserUsage * 100 / twitterUserLimit
    else:
        twitterUserLimit = 'inf'
    twitterHashtagPercent = 0
    twitterHashtagUsage = aspiraUser.twitterHashtagsToHarvest.count()
    if twitterHashtagLimit > 0:
        twitterHashtagPercent = twitterHashtagUsage * 100 / twitterHashtagLimit
    else:
        twitterHashtagLimit = 'inf'
    mostActiveHashtag = "None"
    if twitterHashtagUsage > 0:
        mostActiveHashtag = \
            aspiraUser.twitterHashtagsToHarvest.annotate(harvested_count=Count('harvested_tweets')).order_by(
                    "-harvested_count")[0].hashtag
    return {
        'twitterUserUsage': twitterUserUsage,
        'twitterUserLimit': twitterUserLimit,
        'twitterUserPercent': twitterUserPercent,
        'twitterHashtagUsage': twitterHashtagUsage,
        'twitterHashtagLimit': twitterHashtagLimit,
        'twitterHashtagPercent': twitterHashtagPercent,
        'collectedTweets': collectedTweets,
        'mostActiveTwitterUser': mostActiveTwitterUser,
        'mostActiveHashtag': mostActiveHashtag,
    }


def getYoutubeStats(aspiraUser):
    ytChannelUsage = aspiraUser.ytChannelsToHarvest.count()
    ytChannelLimit = aspiraUser.ytChannelsToHarvestLimit
    ytChannelPercent = 0
    if ytChannelLimit:
        ytChannelPercent = ytChannelUsage * 100 / ytChannelLimit
    else:
        ytChannelLimit = 'inf'

    ytPlaylistUsage = aspiraUser.ytPlaylistsToHarvest.count()
    ytPlaylistLimit = aspiraUser.ytPlaylistsToHarvestLimit
    ytPlaylistPercent = 0
    if ytPlaylistLimit:
        ytPlaylistPercent = ytPlaylistUsage * 100 / ytPlaylistLimit
    else:
        ytPlaylistLimit = 'inf'

    collectedYtVids = YTVideo.objects.filter(channel__harvested_by=aspiraUser).count()
    collectedYtComments = YTChannel.objects.filter(harvested_by=aspiraUser).aggregate(count=Count('comments'))['count']

    mostActiveChannel = aspiraUser.ytChannelsToHarvest.annotate(vidCount=Count('videos')).order_by('vidCount')
    if mostActiveChannel.count():
        mostActiveChannel = mostActiveChannel[0]
    else:
        mostActiveChannel = "None"
    mostActiveYtVid = YTVideo.objects.filter(channel__harvested_by=aspiraUser).order_by('-comment_count')
    if mostActiveYtVid.count():
        mostActiveYtVid = mostActiveYtVid[0]
    else:
        mostActiveYtVid = "None"

    return {
        'ytChannelUsage': ytChannelUsage,
        'ytChannelLimit': ytChannelLimit,
        'ytChannelPercent': ytChannelPercent,
        'ytPlaylistUsage': ytPlaylistUsage,
        'ytPlaylistLimit': ytPlaylistLimit,
        'ytPlaylistPercent': ytPlaylistPercent,
        'collectedYtVids': collectedYtVids,
        'collectedYtComments': collectedYtComments,
        'mostActiveChannel': mostActiveChannel,
        'mostActiveYtVid': mostActiveYtVid,
    }


def getFacebookStats(aspiraUser):
    fbPageUsage = aspiraUser.facebookPagesToHarvest.count()
    fbPageLimit = aspiraUser.facebookPagesToHarvestLimit
    fbPageUsagePercent = 0
    if fbPageLimit:
        fbPageUsagePercent = fbPageUsage * 100 / fbPageLimit
    else:
        fbPageLimit = 'inf'

    collectedFBStatuses = FBPost.objects.filter(from_profile__fbPage__isnull=False) \
        .filter(from_profile__fbPage__harvested_by=aspiraUser).count()
    collectedFBcomments = FBPage.objects.filter(harvested_by=aspiraUser) \
        .aggregate(count=Count('fbProfile__posted_comments'))['count']
    mostActivePage = aspiraUser.facebookPagesToHarvest \
        .annotate(statusCount=Count('fbProfile__postedStatuses')) \
        .order_by('statusCount')
    if mostActivePage.count():
        mostActivePage = mostActivePage[0]
    else:
        mostActivePage = "None"
    mostActiveStatus = FBPost.objects.filter(from_profile__fbPage__isnull=False) \
        .filter(from_profile__fbPage__harvested_by=aspiraUser).order_by('-comment_count')
    if mostActiveStatus.count():
        mostActiveStatus = mostActiveStatus[0]
    else:
        mostActiveStatus = "None"

    return {
        'fbPageUsage': fbPageUsage,
        'fbPageLimit': fbPageLimit,
        'fbPageUsagePercent': fbPageUsagePercent,
        'collectedFBStatuses': collectedFBStatuses,
        'collectedFBcomments': collectedFBcomments,
        'mostActivePage': mostActivePage,
        'mostActiveStatus': mostActiveStatus,
    }


def userLoginPage(request):
    context = {
        'user': request.user,
        'navigator': [
            ('Enregistrement', '#')
        ]
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/login_page.html', context=context)


@login_required()
def userSettings(request):
    context = {
        'user': request.user,
        "navigator": [
            ("Paramètres", "/settings"),
        ],
        "fbAccessToken": None,
    }
    if hasattr(request.user.userProfile, 'fbAccessToken') and \
            request.user.userProfile.fbAccessToken._token:
        context['fbAccessToken'] = request.user.userProfile.fbAccessToken._token
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/settings.html', context)


def resetPWPage(request, token):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    profile = UserProfile.objects.filter(passwordResetToken__exact=token).first()
    if not profile:
        raise Http404

    if profile.passwordResetDateLimit < datetime.utcnow().replace(second=0, microsecond=0, tzinfo=utc):
        raise Http404

    if 'pass1' in request.POST and 'pass2' in request.POST:
        return resetPWConfirm(request, profile)

    return render(request, "AspiraUser/reset_pw_page.html", {
        "navigator": [
            ("Réinitialisation du mot de passe", "#"),
        ],
        'token': token,
    })


@login_required()
def search(request):
    resetUserSelection(request)
    terms = []
    query = ""
    if "query" in request.GET:
        query = request.GET['query']
    terms = digestQuery(query)
    return render(request, "AspiraUser/search_results.html",{
        'user': request.user,
        "navigator": [
            ("Recherche: \"%s\""%"\"+\"".join(terms), "#"),
        ],
        "query": cleanQuery(query),
    })
