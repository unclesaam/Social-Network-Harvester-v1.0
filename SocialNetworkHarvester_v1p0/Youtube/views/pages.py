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
    try:
        channel = YTChannel.objects.filter(pk=identifier).first()
    except:
        channel = None
    if not channel:
        channel = YTChannel.objects.filter(_ident=identifier).first()
    if not channel: raise Http404
    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            ("Chaine: %s"% channel, channel.getLink()),
        ],
        "channel":channel
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'Youtube/YoutubeChannel.html', context)


@login_required()
def videoBase(request, identifier):
    try:
        video = YTVideo.objects.filter(pk=identifier).first()
    except:
        video = None
    if not video:
        video = YTVideo.objects.filter(_ident=identifier).first()
    context = {
        'user': request.user,
        "navigator": [
             ("Youtube", "/youtube"),
            (video.channel, video.channel.getLink()),
            (video, "/youtube/video/%s" % video.getLink()),
        ],
        'video':video,
    }
    return render(request,'Youtube/YoutubeVideo.html', context)


@login_required()
def commentBase(request, identifier):
    try:
        comment = YTComment.objects.filter(pk=identifier).first()
    except:
        comment = None
    if not comment:
        comment = YTComment.objects.filter(_ident=identifier).first()
    if not comment:
        raise Http404
    context = {
        'user': request.user,
        "navigator": comment.navigation_context(),
        'comment': comment,
    }
    return render(request, 'Youtube/YoutubeComment.html', context)


@login_required()
def playlistBase(request, identifier):
    resetUserSelection(request)
    try:
        playlist = YTPlaylist.objects.filter(pk=identifier).first()
    except:
        playlist = None
    if not playlist:
        playlist = YTPlaylist.objects.filter(_ident=identifier).first()
    if not playlist: raise Http404
    displayName = identifier
    if playlist.title:
        displayName = "Liste de lecture: %s"%playlist.title
    channel = playlist.channel

    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            (channel, channel.getLink()),
            (displayName, "/youtube/playlist/%s" % identifier),
        ],
        "playlist": playlist
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'Youtube/YoutubePlaylist.html', context)