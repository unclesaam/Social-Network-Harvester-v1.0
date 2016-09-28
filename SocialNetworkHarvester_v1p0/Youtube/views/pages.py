from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.views import addMessagesToContext
from AspiraUser.models import getUserSelection, resetUserSelection
from Youtube.models import YTChannel, YTVideo, YTComment
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
    context = {
        'user': request.user,
        "navigator": [
            ("Youtube", "/youtube"),
            ("video #"+identifier, "/youtube/video/%s" % identifier),
        ],
    }
    return render(request,'Youtube/YoutubeVideo.html', context)


@login_required()
def commentBase(request, identifier):
	return HttpResponse(identifier)


@login_required()
def playlistBase(request, identifier):
    return HttpResponse(identifier)