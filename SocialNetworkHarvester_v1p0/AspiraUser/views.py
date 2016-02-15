from django.shortcuts import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0


def lastUrlOrHome(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    if request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect('/')

def userDashboard(request):
    context = RequestContext(request, {
        'user': request.user
    })
    print('request.user.is_authenticated = %s'%request.user.is_authenticated())
    return render_to_response('AspiraUser/dashboard.html', context)


def userLogin(request):
    log(request.GET)
    username = request.POST['username']
    pw = request.POST['password']
    user = authenticate(username=username, password=pw)
    if user is not None:
        login(request, user)

    return lastUrlOrHome(request)

def userLoginPage(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('AspiraUser/login_page.html', context)


def userLogout(request):
    logout(request)
    return lastUrlOrHome(request)

@login_required()
def userSettings(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('AspiraUser/settings.html', context)

@login_required()
def editUserSettings(request):
    user = request.user
    for atr in request.POST:
        log("%s: %s"%(atr, request.POST[atr]))
        if atr[0] == 'u':
            setattr(user, atr[2:], request.POST[atr])
        elif atr[0] == 'p':
            setattr(user.userProfile, atr[2:], request.POST[atr])
    user.save()
    user.userProfile.save()

    return userSettings(request)