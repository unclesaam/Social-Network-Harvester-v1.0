from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from tool.views.tables import *
from Youtube.models import *
from AspiraUser.models import getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def ajaxBase(request):
    if not request.user.is_authenticated(): return jsonUnauthorizedError(request)
    if not 'tableId' in request.GET: return jsonBadRequest(request, 'tableId not defined')
    tableId = request.GET['tableId']
    if not (tableId[:2] == 'YT' and tableId in globals()): return jsonBadRequest(request,'Invalid tableId')
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