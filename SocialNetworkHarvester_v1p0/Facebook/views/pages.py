from django.shortcuts import *
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Facebook.models import setFBToken, getFBToken
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS

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
    return render(request,'facebook/FacebookBase.html', context)


@login_required()
def fbUserView(request, FBUserScreenName):
    context = {
        'user': request.user,
        'user_screen_name': FBUserScreenName,
    }
    return render(request,'Facebook/FacebookUser.html', context)


@login_required()
def fbPostView(request, FBPostId):
    context = {
        'user': request.user,
        'postID': FBPostId,
    }
    return render_to_response('Facebook/FacebookPost.html', context)


@login_required()
def fbCommentView(request, FBCommentId):
    context = {
        'user': request.user,
        'commentId': FBCommentId,
    }
    return render(request, 'Facebook/FacebookComment.html', context)


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
