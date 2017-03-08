from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection
from Youtube.models import YTChannel, YTVideo, YTPlaylist, YTPlaylistItem, YTComment
from SocialNetworkHarvester_v1p0.jsonResponses import *
import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def YTselectBase(request):
    tableIdsFunctions = {
        'YTChannelTable': YTChannelTableSelection,
        'YTPlaylistTable': YTPlaylistTableSelection,
        'YTVideosTable': YTVideosTableSelection,
        'YTPlaylistVideosTable': YTPlaylistVideosTableSelection,
        'YTCommentsTable': YTCommentsTableTableSelection,
    }
    return tableIdsFunctions[request.GET['tableId']](request)

def YTChannelTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    queryset = YTChannel.objects.none()
    if select:
        if user.is_staff:
            queryset = YTChannel.objects.filter(harvested_by__isnull=False)
        else:
            queryset = user.userProfile.ytChannelsToHarvest.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def YTPlaylistTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    queryset = YTPlaylist.objects.none()
    if select:
        if user.is_staff:
            queryset = YTPlaylist.objects.filter(harvested_by__isnull=False)
        else:
            queryset = user.userProfile.ytPlaylistsToHarvest.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


#@viewsLogger.debug()
def YTVideosTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    selectedChannels = tableRowsSelection.getSavedQueryset('YTChannel', 'YTChannelTable')
    selectedPlaylists = tableRowsSelection.getSavedQueryset('YTPlaylist', 'YTPlaylistTable')
    queryset = YTVideo.objects.none()
    if select:
        for channel in selectedChannels:
            queryset = queryset | channel.videos.all()
        for playlist in selectedPlaylists:
            items = playlist.items.all()
            queryset = queryset | YTVideo.objects.filter(playlistsSpots__pk__in=items)
    queryset = queryset.filter(title__isnull=False)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def YTPlaylistVideosTableSelection(request):
    match = re.match(r'/youtube/playlist/(?P<playlistId>[\w\._-]+)/?.*',request.GET['pageURL'])
    if not match: return jsonBadRequest(request, 'invalid pageURL parameter')
    if not YTPlaylist.objects.filter(_ident=match.group('playlistId')).exists():
        return jsonNotFound(request)
    playlist = YTPlaylist.objects.get(_ident=match.group('playlistId'))
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    queryset = YTPlaylistItem.objects.none()
    if select: queryset = playlist.items.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def YTCommentsTableTableSelection(request):
    match = re.match(r'/youtube/video/(?P<videoId>[\w\._-]+)/?.*', request.GET['pageURL'])
    if not match: return jsonBadRequest(request, 'invalid pageURL parameter')
    if not YTVideo.objects.filter(_ident=match.group('videoId')).exists():
        return jsonNotFound(request)
    video = YTVideo.objects.get(_ident=match.group('videoId'))
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    queryset = YTComment.objects.none()
    if select: queryset = video.comments.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])

