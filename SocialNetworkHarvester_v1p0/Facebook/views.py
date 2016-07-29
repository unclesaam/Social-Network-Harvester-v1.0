from django.shortcuts import *
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Facebook.models import setFBToken, getFBToken

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


@login_required()
def facebookBase(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('facebook/FacebookBase.html', context)


@login_required()
def fbUserView(request, FBUserScreenName):
    context = RequestContext(request, {
        'user': request.user,
        'user_screen_name': FBUserScreenName,
    })
    return render_to_response('Facebook/FacebookUser.html', context)


@login_required()
def fbPostView(request, FBPostId):
    context = RequestContext(request, {
        'user': request.user,
        'postID': FBPostId,
    })
    return render_to_response('Facebook/FacebookPost.html', context)


@login_required()
def fbCommentView(request, FBCommentId):
    context = RequestContext(request, {
        'user': request.user,
        'commentId': FBCommentId,
    })
    return render_to_response('Facebook/FacebookComment.html', context)


@login_required()
def ajaxFbUserTable(request, aspiraUserId):
    pass


@login_required()
def ajaxFbPostTable(request, aspiraUserId):
    pass


@login_required()
def ajaxFbCommentTable(request, aspiraUserId):
    pass


@login_required()
def fbTestPage(request):
    if not request.user.is_superuser:
        raise Http404()
    return render_to_response('Facebook/FacebookTest.html', RequestContext(request, {'user' : request.user}))


@login_required()
@csrf_exempt
def setAPIToken(request):
    if not request.user.is_superuser:
        raise Http404()
    setFBToken(request.POST['token'])
    return HttpResponse('worked!')
