from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.views import addMessagesToContext
from AspiraUser.models import getUserSelection, resetUserSelection
from Youtube.models import YTChannel, YTVideo, YTComment, YTPlaylist
import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

@login_required()
def youtubeBase(request):
	context = {
		'user': request.user,
		"navigator": [
			("Youtube", "/youtube"),
		]
	}
	request, context = addMessagesToContext(request, context)
	resetUserSelection(request)
	return render(request, 'Youtube/YoutubeBase.html', context)


@login_required()
def channelBase(request, identifier):
    resetUserSelection(request)
    channel = None
    if YTChannel.objects.filter(_ident=identifier).exists():
        channel = YTChannel.objects.get(_ident=identifier)
    if not channel: raise Http404
    displayName = identifier
    if channel.title:
        displayName = channel.title
    elif channel.userName:
        displayName.userName
    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            (displayName, "/youtube/channel/%s"%identifier),
        ],
        "channel":channel
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'Youtube/YoutubeChannel.html', context)


@login_required()
def videoBase(request, identifier):
    if not YTVideo.objects.filter(_ident=identifier).exists():
        raise Http404
    video = YTVideo.objects.get(_ident=identifier)
    context = {
        'user': request.user,
        "navigator": [
             ("Youtube", "/youtube"),
            (video.channel, "/youtube/channel/%s"% video.channel._ident),
            (video.title, "/youtube/video/%s" % identifier),
        ],
        'video':video,
    }
    return render(request,'Youtube/YoutubeVideo.html', context)


@login_required()
def commentBase(request, identifier):
    if not YTComment.objects.filter(_ident=identifier).exists():
        raise Http404
    comment = YTComment.objects.get(_ident=identifier)
    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            (comment.author, "/youtube/channel/%s" % comment.author._ident),
            ('Comment #%s'%identifier, "/youtube/comment/%s" % identifier),
        ],
        'comment': comment,
    }
    return render(request, 'Youtube/YoutubeComment.html', context)


@login_required()
def playlistBase(request, identifier):
    resetUserSelection(request)
    playlist = None
    if YTPlaylist.objects.filter(_ident=identifier).exists():
        playlist = YTPlaylist.objects.get(_ident=identifier)
    if not playlist: raise Http404
    displayName = identifier
    if playlist.title:
        displayName = "Playlist: %s"%playlist.title
    channel = playlist.channel
    if channel:
        channelURL = "/youtube/channel/%s" % channel._ident
    else:
        channel = 'Undefined channel'
        channelURL = '#'

    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            (channel, channelURL),
            (displayName, "/youtube/playlist/%s" % identifier),
        ],
        "playlist": playlist
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'Youtube/YoutubePlaylist.html', context)