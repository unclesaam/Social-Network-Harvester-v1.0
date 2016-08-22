from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection
from Youtube.models import YTChannel, YTVideo

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def YTselectBase(request):
    tableIdsFunctions = {
        'YTChannelTable': YTChannelTableSelection,

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