from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from AspiraUser.models import getUserSelection, resetUserSelection
import re
from Youtube.models import *
from tool.views.tables import readLinesFromCSV

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


plurial = lambda i: 's' if int(i)>1 else ''


validFormNames = [
        'YTAddChannel',
        'YTRemoveChannel',
        'YTAddPlaylist',
        'YTRemovePlaylist',
    ]


@login_required()
def formBase(request, formName):
    if not request.user.is_authenticated(): return jsonUnauthorizedError(request)
    if not formName in validFormNames: return jsonBadRequest(request, 'Specified form does not exists')
    try:
        return globals()[formName](request)
    except:
        viewsLogger.exception("ERROR OCCURED IN YOUTUBE AJAX WITH FORM NAME '%s'" % formName)
        return jsonUnknownError(request)


def YTAddChannel(request):
    if not 'channelURL' in request.POST and not 'Browse' in request.FILES : return jsonBadRequest(request, 'No channel url specified')
    limit = request.user.userProfile.ytChannelsToHarvestLimit
    currentCount = request.user.userProfile.ytChannelsToHarvest.count()
    if limit <= currentCount:
        return jResponse({
            'status': 'exception',
            'errors': ["Vous avez atteint la limite de chaînes à collecter permise."],
        })
    channelUrls = request.POST.getlist('channelURL')
    invalids = []
    if 'Browse' in request.FILES:
        fileUrls, errors = readLinesFromCSV(request)
        channelUrls += fileUrls
        invalids += errors
    if limit <= currentCount+len(channelUrls):
        channelUrls = channelUrls[:limit-currentCount]
    invalids += addPlaylists(request, channelUrls)

    numChannelAdded = len(channelUrls) - len(invalids)
    if not numChannelAdded:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas une URL de chaîne valide'%url for url in invalids],
        })
    return jResponse({
        'status':'ok',
        'messages': ['%s chaînes%s ont été ajoutées à votre liste (%i erreurs%s)'%(numChannelAdded, plurial(numChannelAdded),
                                                                            len(invalids), plurial(len(invalids)))]
    })

#@viewsLogger.debug(showArgs=True)
def addChannels(request,channelUrls):
    profile = request.user.userProfile
    invalids = []
    for url in channelUrls:
        newChannel = None
        match = re.match(r'https?://www.youtube.com/user/(?P<username>[\w\.-]+)/?.*',url)
        if match:
            newChannel,new = YTChannel.objects.get_or_create(userName=match.group('username'))
        else:
            match = re.match(r'https?://www.youtube.com/channel/(?P<channelId>[\w\.-]+)/?.*', url)
            if match:
                newChannel,new = YTChannel.objects.get_or_create(_ident=match.group('channelId'))
            else:
                invalids.append(url)
        if newChannel:
            profile.ytChannelsToHarvest.add(newChannel)
            profile.save()
    return invalids


def YTRemoveChannel(request):
    return jsonNotImplementedError(request)


#@viewsLogger.debug(showArgs=True)
def YTAddPlaylist(request):
    if not 'playlistURL' in request.POST and not 'Browse' in request.FILES: return jsonBadRequest(request,
                                                                                                 'No playlist url specified')
    limit = request.user.userProfile.ytPlaylistsToHarvestLimit
    currentCount = request.user.userProfile.ytPlaylistsToHarvest.count()
    if limit <= currentCount:
        return jResponse({
            'status': 'exception',
            'errors': ["Vous avez atteint la limite de playlists à collecter permise."],
        })
    playlistURLs = request.POST.getlist('playlistURL')
    invalids = []
    if 'Browse' in request.FILES:
        fileUrls, errors = readLinesFromCSV(request)
        playlistURLs += fileUrls
        invalids += errors
    if limit <= currentCount + len(playlistURLs):
        playlistURLs = playlistURLs[:limit - currentCount]
    invalids += addPlaylists(request, playlistURLs)

    numPlaylistAdded = len(playlistURLs) - len(invalids)
    if not numPlaylistAdded:
        return jResponse({
            'status': 'exception',
            'errors': ['"%s" n\'est pas une URL de playlist valide' % url for url in invalids],
        })
    return jResponse({
        'status': 'ok',
        'messages': ['%s playlists%s ont été ajoutées à votre liste (%i erreurs%s)' % (
            numPlaylistAdded, plurial(numPlaylistAdded),len(invalids), plurial(len(invalids)))]
    })


@viewsLogger.debug(showArgs=True)
def addPlaylists(request, playlistURLs):
    profile = request.user.userProfile
    invalids = []
    for url in playlistURLs:
        newPlaylist = None
        match = re.match(r'.*list=(?P<ident>[\w\.-]+)&?.*', url)
        log(url)
        if match:
            log('match!')
            log(match.group('ident'))
            newPlaylist, new = YTPlaylist.objects.get_or_create(_ident=match.group('ident'))
            profile.ytPlaylistsToHarvest.add(newPlaylist)
            profile.save()
        else:
            invalids.append(url)
    return invalids

def YTRemovePlaylist(request):
    return jsonNotImplementedError(request)