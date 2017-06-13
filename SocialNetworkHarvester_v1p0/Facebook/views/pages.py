from django.shortcuts import *
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS
from AspiraUser.models import resetUserSelection
from Facebook.models import FBPage, FBUser, FBProfile, FBComment, FBPost

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


@login_required()
def facebookBase(request):
    context = {
        'user': request.user,
        "navigator": [
            ("Facebook", "/facebook"),
        ],
    }
    resetUserSelection(request)
    return render(request,'Facebook/FacebookBase.html', context)


@login_required()
def fbUserView(request, FBUserId):
    fbUser = FBUser.objects.filter(pk=FBUserId)
    if not fbUser:
        fbUser = FBUser.objects.filter(_ident=FBUserId)
    if not fbUser:
        raise Http404
    else: fbUser = fbUser[0]
    context = {
        'user': request.user,
        'fbUser':fbUser,
        "navigator": [
            ("Facebook", "/facebook"),
            (fbUser, "/facebook/user/%s"%FBUserId),
        ],
    }
    resetUserSelection(request)
    return render(request,'Facebook/FacebookUser.html', context)

@login_required()
def fbPageView(request, FBPageId):
    fbPage = FBPage.objects.filter(pk=FBPageId)
    if not fbPage:
        fbPage = FBPage.objects.filter(_ident=FBPageId)
    if not fbPage:
        raise Http404
    else: fbPage = fbPage[0]
    context = {
        'user':request.user,
        'page': fbPage,
        'FBPageId':FBPageId,
        "navigator": [
            ("Facebook", "/facebook"),
            (fbPage, "/facebook/page/%s"%FBPageId),
        ],
    }
    resetUserSelection(request)
    return render(request,'Facebook/FacebookPage.html', context)


@login_required()
def fbPostView(request, FBPostId):
    fbPost = FBPost.objects.filter(pk=FBPostId)
    if not fbPost:
        fbPost = FBPost.objects.filter(_ident=FBPostId)
    if not fbPost:
        raise Http404
    else: fbPost = fbPost[0]
    context = {
        'fbPost':fbPost,
        'user': request.user,
        "navigator": [
            ("Facebook", "/facebook"),
            (fbPost.from_profile, fbPost.from_profile.getLink),
            ("%s Facebook"%fbPost.getTypeFrench(), "/facebook/post/%s"%fbPost.pk)
        ],
    }
    resetUserSelection(request)
    return render_to_response('Facebook/FacebookPost.html', context)


@login_required()
def fbCommentView(request, FBCommentId):
    fbComment = FBComment.objects.filter(pk=FBCommentId)
    if not fbComment:
        fbComment = FBComment.objects.filter(_ident=FBCommentId)
    if not fbComment:
        raise Http404
    else: fbComment = fbComment[0]
    context = {
        'fbComment':fbComment,
        'user': request.user,
        "navigator": [
            ("Facebook", "/facebook"),
            (fbComment.from_profile, fbComment.from_profile.getLink),
            ("Commentaire facebook", "/facebook/post/%s"%fbComment.pk)
        ],
    }
    resetUserSelection(request)
    return render_to_response('Facebook/FacebookComment.html', context)


@login_required()
def APILoginPage(request):
    if not request.user.is_superuser:
        raise Http404()
    context = {'user': request.user,
                'app': FACEBOOK_APP_PARAMS
            }
    return render_to_response('Facebook/FacebookLogin.html', context)


@login_required()
@csrf_exempt
def setAPIToken(request):
    if not request.user.is_superuser:
        raise Http404()
    setFBToken(request.POST['token'])
    return HttpResponse('worked!')
