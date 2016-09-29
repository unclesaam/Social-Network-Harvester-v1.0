from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from tool.views.tables import *
from Youtube.models import *
from AspiraUser.models import getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

validTableIds = [
    'YTChannelTable',
    'YTChannelVideosTable',
    'YTVideosTable',
    'YTPlaylistTable',
    'YTPlaylistVideosTable',
]

@login_required()
def ajaxBase(request):
    if not request.user.is_authenticated(): return jsonUnauthorizedError(request)
    if not 'tableId' in request.GET: return jsonBadRequest(request, 'tableId not defined')
    tableId = request.GET['tableId']
    if not tableId in validTableIds: return jsonBadRequest(request, 'Wrong tableId defined')
    try:
        return globals()[tableId](request)
    except:
        viewsLogger.exception("ERROR OCCURED IN YOUTUBE AJAX WITH TABLEID=%s"% tableId)
        return jsonUnknownError(request)

def YTChannelTable(request):
    aspiraUser = request.user
    if aspiraUser.is_staff:
        queryset = YTChannel.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.ytChannelsToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("YTChannel", 'YTChannelTable')
    return ajaxResponse(queryset, request, selecteds)



#@viewsLogger.debug(showArgs=True)
def YTChannelVideosTable(request):
    if not 'channelTitle' in request.GET: return jsonBadRequest(request,'no channel title specified')
    if not YTChannel.objects.filter(title=request.GET['channelTitle']).exists():
        return jsonNotFound(request)
    channel = YTChannel.objects.get(title=request.GET['channelTitle'])
    queryset = channel.videos.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("YTVideo", 'YTChannelVideosTable')
    return ajaxResponse(queryset, request, selecteds)


#@viewsLogger.debug(showArgs=True)
def YTVideosTable(request):
    user = request.user
    tableRowsSelections = getUserSelection(request)
    selectedChannels = tableRowsSelections.getSavedQueryset('YTChannel', 'YTChannelTable')
    selectedPlaylists = tableRowsSelections.getSavedQueryset('YTPlaylist', 'YTPlaylistTable')
    queryset = YTVideo.objects.none()
    for channel in selectedChannels:
        queryset = queryset | channel.videos.all()
    for playlist in selectedPlaylists:
        items = playlist.items.all()
        queryset = queryset | YTVideo.objects.filter(playlistsSpots__pk__in=items)
    selectedVideos = tableRowsSelections.getSavedQueryset("YTVideo", 'YTVideosTable')
    queryset = queryset | selectedVideos
    return ajaxResponse(queryset.distinct(), request, selectedVideos)


#@viewsLogger.debug(showArgs=True)
def YTPlaylistTable(request):
    user = request.user
    tableRowsSelections = getUserSelection(request)
    queryset = user.userProfile.ytPlaylistsToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selectedPlaylists = tableRowsSelections.getSavedQueryset("YTPlaylist", 'YTPlaylistTable')
    return ajaxResponse(queryset, request, selectedPlaylists)


def YTPlaylistVideosTable(request):
    if not 'playlist' in request.GET: return jsonBadRequest(request, 'no playlist id specified')
    if not YTPlaylist.objects.filter(_ident=request.GET['playlist']).exists():
        return jsonNotFound(request)
    playlist = YTPlaylist.objects.get(_ident=request.GET['playlist'])
    queryset = playlist.items.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("YTPlaylistItem", 'YTPlaylistVideosTable')
    return ajaxResponse(queryset, request, selecteds)
