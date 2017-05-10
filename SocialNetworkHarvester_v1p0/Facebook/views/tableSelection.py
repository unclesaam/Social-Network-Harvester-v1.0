from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection
from Facebook.models import FBPage, FBPost
from SocialNetworkHarvester_v1p0.jsonResponses import *
import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def FBselectBase(request):
    tableIdsFunctions = {
        'FbPagesTable': FbPageTableSelection,
        'FBPostTable': FBPostTableSelection,

    }
    return tableIdsFunctions[request.GET['tableId']](request)



def FbPageTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    queryset = FBPage.objects.none()
    if select:
        if user.is_staff:
            queryset = FBPage.objects.filter(harvested_by__isnull=False)
        else:
            queryset = user.userProfile.facebookPagesToHarvest.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def FBPostTableSelection(request):
    select = 'selected' in request.GET
    queryset = FBPost.objects.none()
    tableRowsSelection = getUserSelection(request)
    if select:
        selectedFBPages = tableRowsSelection.getSavedQueryset('FBPage', 'FbPagesTable')
        for fbPage in selectedFBPages:
            queryset = queryset | fbPage.fbProfile.postedStatuses.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])