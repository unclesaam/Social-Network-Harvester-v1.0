from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection
from Facebook.models import FBPage, FBPost, FBComment
from SocialNetworkHarvester_v1p0.jsonResponses import *
import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def FBselectBase(request):
    tableIdsFunctions = {
        'FbPagesTable': FbPageTableSelection,
        'FBPostTable': FBPostTableSelection,
        'FBCommentTable':FBCommentTableSelection,
        'FBPageFeedTable':FBPageFeedTableSelection,
        'FBPagePostedTable':FBPagePostedTableSelection,
        'FBPostCommentTable':FBPostCommentTableSelection,
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

def FBCommentTableSelection(request):
    select = 'selected' in request.GET
    queryset = FBComment.objects.none()
    tableRowsSelection = getUserSelection(request)
    if select:
        selectedFBPosts = tableRowsSelection.getSavedQueryset('FBPost', 'FBPostTable')
        for fbPost in selectedFBPosts:
            queryset = queryset | fbPost.fbComments.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])

def FBPageFeedTableSelection(request):
    select = 'selected' in request.GET
    pageIdent = request.GET['pageURL'].split('/')[-1]
    fbPage = get_from_any_or_404(FBPage,_ident=pageIdent, pk=pageIdent)
    queryset = FBPost.objects.none()
    if select:
        queryset = fbPage.fbProfile.targetedByStatuses.all()
    getUserSelection(request).saveQuerySet(queryset, request.GET['tableId'])

def FBPagePostedTableSelection(request):
    select = 'selected' in request.GET
    pageIdent = request.GET['pageURL'].split('/')[-1]
    fbPage = get_from_any_or_404(FBPage,_ident=pageIdent, pk=pageIdent)
    queryset = FBPost.objects.none()
    if select:
        queryset = fbPage.fbProfile.postedStatuses.all()
    getUserSelection(request).saveQuerySet(queryset, request.GET['tableId'])

def FBPostCommentTableSelection(request):
    select = 'selected' in request.GET
    pageIdent = request.GET['pageURL'].split('/')[-1]
    fbPost = get_from_any_or_404(FBPost,_ident=pageIdent, pk=pageIdent)
    queryset = FBPost.objects.none()
    if select:
        queryset = fbPost.fbComments.all()
    getUserSelection(request).saveQuerySet(queryset, request.GET['tableId'])






############## UTIL ###############
def get_from_any_or_404(table, **kwargs):
    kwargs = {kwarg: kwargs[kwarg] for kwarg in kwargs.keys() if kwargs[kwarg]}  # eliminate "None" values
    item = None
    for param in kwargs.keys():
        if item: break
        try:
            item = table.objects.get(**{param: kwargs[param]})
        except:
            continue
    if not item: raise Http404()
    return item