from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from tool.views.tables import *
from Facebook.models import *
from AspiraUser.models import getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG

log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0
logerror = lambda s: viewsLogger.exception(s) if DEBUG else 0

validTableIds = [
    'FbPagesTable',
    'FBPostTable',
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
        viewsLogger.exception( "ERROR OCCURED IN YOUTUBE AJAX WITH TABLEID=%s"% tableId)
        return jsonUnknownError(request)


#@viewsLogger.debug()
def FbPagesTable(request):
    aspiraUser = request.user
    if aspiraUser.is_staff:
        queryset = FBPage.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.facebookPagesToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("FBPage", 'FbPagesTable')
    return ajaxResponse(queryset, request, selecteds)


def FBPostTable(request):
    queryset = FBPost.objects.none()
    tableRowsSelections = getUserSelection(request)
    selectedFBPages = tableRowsSelections.getSavedQueryset('FBPage', 'FbPagesTable')
    queryset = tableRowsSelections.getSavedQueryset('FBPost', 'FBPostTable')
    for fbPage in selectedFBPages:
        queryset = queryset | fbPage.fbProfile.postedStatuses.all()
    selecteds = tableRowsSelections.getSavedQueryset("FBPost", 'FBPostTable')
    return ajaxResponse(queryset.distinct(), request, selecteds)