from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Count
from django.shortcuts import *
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth import authenticate

#from Facebook.views.tableSelection import FBselectBase
from SocialNetworkHarvester_v1p0.jsonResponses import *
from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
from Twitter.models import *
from Youtube.models import *
from Facebook.models import *
from .models import UserProfile, getUserSelection, resetUserSelection
from datetime import datetime, timedelta
from django.utils.timezone import utc

log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0


def lastUrlOrHome(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    if request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect('/')

def addMessagesToContext(request, context):
    if 'aspiraErrors' in request.session:
        context['aspiraErrors'] = request.session['aspiraErrors']
    if 'aspiraMessages' in request.session:
        context['aspiraMessages'] = request.session['aspiraMessages']
    request.session['aspiraMessages'] = []
    request.session['aspiraErrors'] = []
    return request, context

@login_required()
def userDashboard(request):
    resetUserSelection(request)
    aspiraUser = request.user.userProfile
    context = {
        'user': request.user,
        "navigator":[
            ("Tableau de bord", "/"),
        ],
        "twStats":getTwitterStats(aspiraUser),
        "ytStats": getYoutubeStats(aspiraUser),
        "fbStats": getFacebookStats(aspiraUser),
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/dashboard.html', context)


def getTwitterStats(aspiraUser):
    twitterUserLimit = aspiraUser.twitterUsersToHarvestLimit
    twitterHashtagLimit = aspiraUser.twitterHashtagToHarvestLimit
    collectedTweets = Tweet.objects.filter(user__harvested_by=aspiraUser).count() + \
                      Tweet.objects.filter(harvested_by__harvested_by=aspiraUser).count()
    mostActiveTwitterUser = "None"
    twitterUserUsage = aspiraUser.twitterUsersToHarvest.count()
    if twitterUserUsage > 0:
        mostActiveTwitterUser = \
        aspiraUser.twitterUsersToHarvest.annotate(harvested_count=Count('tweets')).order_by("-harvested_count")[0]
    twitterUserPercent = 0
    if twitterUserLimit > 0:
        twitterUserPercent = twitterUserUsage * 100 / twitterUserLimit
    else:
        twitterUserLimit = 'inf'
    twitterHashtagPercent = 0
    twitterHashtagUsage = aspiraUser.twitterHashtagsToHarvest.count()
    if twitterHashtagLimit > 0:
        twitterHashtagPercent = twitterHashtagUsage * 100 / twitterHashtagLimit
    else:
        twitterHashtagLimit = 'inf'
    mostActiveHashtag = "None"
    if twitterHashtagUsage > 0:
        mostActiveHashtag = \
        aspiraUser.twitterHashtagsToHarvest.annotate(harvested_count=Count('harvested_tweets')).order_by(
            "-harvested_count")[0].hashtag
    return {
        'twitterUserUsage': twitterUserUsage,
        'twitterUserLimit':twitterUserLimit,
        'twitterUserPercent':twitterUserPercent,
        'twitterHashtagUsage': twitterHashtagUsage,
        'twitterHashtagLimit':twitterHashtagLimit,
        'twitterHashtagPercent':twitterHashtagPercent,
        'collectedTweets':collectedTweets,
        'mostActiveTwitterUser':mostActiveTwitterUser,
        'mostActiveHashtag':mostActiveHashtag,
    }

def getYoutubeStats(aspiraUser):
    ytChannelUsage = aspiraUser.ytChannelsToHarvest.count()
    ytChannelLimit = aspiraUser.ytChannelsToHarvestLimit
    ytChannelPercent = 0
    if ytChannelLimit:
        ytChannelPercent = ytChannelUsage*100/ytChannelLimit
    else:
        ytChannelLimit = 'inf'

    ytPlaylistUsage = aspiraUser.ytPlaylistsToHarvest.count()
    ytPlaylistLimit = aspiraUser.ytPlaylistsToHarvestLimit
    ytPlaylistPercent = 0
    if ytPlaylistLimit:
        ytPlaylistPercent = ytPlaylistUsage * 100 / ytPlaylistLimit
    else:
        ytPlaylistLimit = 'inf'

    collectedYtVids = YTVideo.objects.filter(channel__harvested_by=aspiraUser).count()
    collectedYtComments = YTChannel.objects.filter(harvested_by=aspiraUser).aggregate(count=Count('comments'))['count']

    mostActiveChannel = aspiraUser.ytChannelsToHarvest.annotate(vidCount=Count('videos')).order_by('vidCount')
    if mostActiveChannel.count() :
        mostActiveChannel = mostActiveChannel[0]
    else:
        mostActiveChannel = "None"
    mostActiveYtVid = YTVideo.objects.filter(channel__harvested_by=aspiraUser).order_by('-comment_count')
    if mostActiveYtVid.count():
        mostActiveYtVid = mostActiveYtVid[0]
    else:
        mostActiveYtVid = "None"

    return {
        'ytChannelUsage':ytChannelUsage,
        'ytChannelLimit':ytChannelLimit,
        'ytChannelPercent':ytChannelPercent,
        'ytPlaylistUsage':ytPlaylistUsage,
        'ytPlaylistLimit':ytPlaylistLimit,
        'ytPlaylistPercent':ytPlaylistPercent,
        'collectedYtVids':collectedYtVids,
        'collectedYtComments':collectedYtComments,
        'mostActiveChannel':mostActiveChannel,
        'mostActiveYtVid':mostActiveYtVid,
    }

def getFacebookStats(aspiraUser):
    fbPageUsage = aspiraUser.facebookPagesToHarvest.count()
    fbPageLimit = aspiraUser.facebookPagesToHarvestLimit
    fbPageUsagePercent = 0
    if fbPageLimit:
        fbPageUsagePercent = fbPageUsage*100/fbPageLimit
    else:
        fbPageLimit = 'inf'

    collectedFBStatuses = FBPost.objects.filter(from_profile__fbPage__isnull=False)\
            .filter(from_profile__fbPage__harvested_by=aspiraUser).count()
    collectedFBcomments = FBPage.objects.filter(harvested_by=aspiraUser)\
            .aggregate(count=Count('fbProfile__posted_comments'))['count']
    mostActivePage = aspiraUser.facebookPagesToHarvest\
            .annotate(statusCount=Count('fbProfile__postedStatuses'))\
            .order_by('statusCount')
    if mostActivePage.count() :
        mostActivePage = mostActivePage[0]
    else:
        mostActivePage = "None"
    mostActiveStatus = FBPost.objects.filter(from_profile__fbPage__isnull=False)\
        .filter(from_profile__fbPage__harvested_by=aspiraUser).order_by('-comment_count')
    if mostActiveStatus.count():
        mostActiveStatus = mostActiveStatus[0]
    else:
        mostActiveStatus = "None"

    return {
        'fbPageUsage':fbPageUsage,
        'fbPageLimit':fbPageLimit,
        'fbPageUsagePercent':fbPageUsagePercent,
        'collectedFBStatuses':collectedFBStatuses,
        'collectedFBcomments':collectedFBcomments,
        'mostActivePage':mostActivePage,
        'mostActiveStatus':mostActiveStatus,
    }


def userLogin(request):
    username = request.POST['username']
    pw = request.POST['password']
    user = authenticate(username=username, password=pw)
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            request.session['aspiraErrors'] = ['Ce nom d\'utilisateur existe, mais le compte est présentement inactif. Est-ce que le webmaster vous a contacté?']
    else:
        request.session['aspiraErrors'] = ['Invalid login information']

    return lastUrlOrHome(request)

def userLoginPage(request):
    context = {
        'user': request.user,
        'navigator':[
            ('Enregistrement','#')
        ]
    }
    request, context = addMessagesToContext(request, context)
    return render(request,'AspiraUser/login_page.html', context=context)


@login_required()
def userLogout(request):
    for select in request.user.tableRowsSelections.all():
        select.delete()
    logout(request)
    return lastUrlOrHome(request)

@login_required()
def userSettings(request):
    context = {
        'user': request.user,
        "navigator":[
            ("Paramètres", "/settings"),
        ],
        "fbAccessToken":None,
    }
    if hasattr(request.user.userProfile, 'fbAccessToken') and \
            request.user.userProfile.fbAccessToken._token:
        context['fbAccessToken'] = request.user.userProfile.fbAccessToken._token
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/settings.html', context)

#@viewsLogger.debug()
@login_required()
def editUserSettings(request):
    user = request.user
    #pretty(request.POST)
    for atr in request.POST:
        if atr not in [
            'u_first_name',
            'u_last_name',
            'u_email',
            'p_twitterApp_consumerKey',
            'p_twitterApp_consumer_secret',
            'p_twitterApp_access_token_key',
            'p_twitterApp_access_token_secret',
            'p_youtubeApp_dev_key'
        ] and not atr == 'csrfmiddlewaretoken':
            request.session['aspiraErrors'] = ['Une erreur est survenue. Veuillez contacter l\'administrateur.']
            return userSettings(request)
        if atr[0] == 'u':
            setattr(user, atr[2:], request.POST[atr])
        elif atr[0] == 'p':
            setattr(user.userProfile, atr[2:], request.POST[atr])
    user.save()
    user.userProfile.twitterApp_parameters_error = False
    user.userProfile.facebookApp_parameters_error = False
    user.userProfile.youtubeApp_parameters_error = False
    user.userProfile.save()
    request.session['aspiraMessages'] = ['Vos paramètres ont été mis à jour. Merci!']
    return userSettings(request)


def userRegister(request):
    #TODO: Refuse usernames containing spaces, accents and such.
    data = request.POST
    aspiraErrors = []
    masterAddrs = [user.email for user in User.objects.filter(is_superuser=True, email__isnull=False) if
                   user.email != '']
    required_fields = {'username':'Username',
                       'email': 'Email address',
                       'pw': 'Password'}
    context = {
        'user': request.user,
        'navigator': [
            ('Enregistrement', '#')
        ]
    }

    for field in required_fields.keys():
        if field not in data or data[field] == '':
            aspiraErrors.append('Le champ "%s" est vide! Veuillez y insérer une valeur.'% required_fields[field])

    if not aspiraErrors and data['pw'] != data['pw_confirm']:
        aspiraErrors.append('Les mots de passe ne coincident pas!')

    if not aspiraErrors and len(data['pw']) < 6:
        aspiraErrors.append('Votre mot de passe doit avoir au moins 6 caractères.')

    if not aspiraErrors and User.objects.filter(email=data['email']).exists():
        aspiraErrors.append('Un compte avec cette adresse email existe déjà!')

    if not aspiraErrors and User.objects.filter(username=data['username']).exists():
        aspiraErrors.append('Un compte avec ce nom d\'utilisateur existe déjà!')

    if not aspiraErrors and not validate_userName(data['username']):
        aspiraErrors.append('Le nom d\'utilisateur ne peut contenir que des caractères alphanumériques.')

    if not aspiraErrors:
        try:
            validate_email(data['email'])
        except ValidationError:
            aspiraErrors.append('L\'adresse email fournie ne semble pas valide. Veuillez vérifier qu\'il '
                                'ne s\'agit pas d\'une erreur.')

    if not aspiraErrors:
        message = render_to_string('AspiraUser/emails/newAccountInstructions.html', {
            'username': data['username'],
            'fname': data['fname'],
            'lname': data['lname'],
            'org': data['org'],
            'webmasters': masterAddrs,
        })
        send_mail('SNH - Account creation instructions', 'message',
              'doNotReplyMail', [data['email']], html_message=message)

    if not aspiraErrors:
        try:
            newUser = User.objects.create_user(data['username'],data['email'],data['pw'],
                first_name=data['fname'],
                last_name=data['lname'],
                is_active=False
            )
            newProfile = UserProfile.objects.create(user=newUser)
        except:
            viewsLogger.exception('An error occured while creating a new AspiraUser!')
            aspiraErrors.append('An error occured! Please contact the webmaster directly to create your account.')

    if not aspiraErrors:
        message = render_to_string('AspiraUser/emails/validateNewAccount.html', {
            'email':data['email'],
            'username':data['username'],
            'fname':data['fname'],
            'lname':data['lname'],
            'org':data['org'],
            'usageText':data['usageText'],
            'adminAuth': "https://%s/adminauth/user/%s/change/"%(request.get_host(), newUser.pk)
        })

        try:
            send_mail('SNH - New account creation request', 'message',
                  'doNotReplyMail', masterAddrs, html_message=message)
        except:
            viewsLogger.exception('An error occured while sending an email to %s'% masterAddrs)

    if aspiraErrors:
        request.session['aspiraErrors'] = aspiraErrors
        fieldKeeper = {}
        for field in ['fname', 'username', 'org', 'email', 'lname', 'usageText']:
            if field in data:
                fieldKeeper[field] = data[field]
        context['fieldKeeper'] = fieldKeeper
        template = 'AspiraUser/login_page.html'
    else:
        request.session['aspiraMessages'] = ["Merci! Vous reçevrez un courriel aussitôt que votre compte est approuvé "+
                                             "par le webmaster."]
        template = 'AspiraUser/register_successful.html'
    request, context = addMessagesToContext(request, context)
    return render(request, template, context)


def validate_userName(userName):
    return re.match(r'^[_a-zA-Z0-9]+$', userName)

def confAgreement(request):
    return render(request, 'AspiraUser/confidentPol.html',{})


def browserList(request):
    return render(request, "AspiraUser/browserList.html",{})


@login_required()
def removeSelectedItems(request):
    aspiraErrors = []
    userProfile = request.user.userProfile
    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(None, request.GET['tableId'])
    successNum = 0
    listToRemovefrom = getattr(userProfile, request.GET['listToRemoveFrom'])
    for item in queryset:
        try:
            listToRemovefrom.remove(item)
            successNum += 1
        except:
            aspiraErrors.append('Something weird has happened while removing %s' % item)
    if aspiraErrors == []:
        response = {'status': 'ok', 'messages': [
            'Removed %i item%s from your list' % (successNum, 's' if successNum > 1 else '')]}
    else:
        response = {'status': 'exception', 'errors': aspiraErrors}
    selection.delete()
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required()
def updatePW(request):
    user = request.user
    if not all(
        ['pass0' in request.POST, 'pass1' in request.POST, 'pass2' in request.POST]):
        return jResponse({'status': 'error',
                          'errors': ['Requête invalide']})

    if not user.check_password(request.POST['pass0']):
        return jsonErrors('Mauvais mot de passe actuel')

    if user.check_password(request.POST['pass1']):
        return jsonErrors('Le nouveau mot de passe doit être différent du mot de passe actuel')

    if len(request.POST['pass1'])<6:
        return jsonErrors('Le mot de passe doit contenir au moins 6 caractères.')

    if request.POST['pass1'] != request.POST['pass2'] :
        return jsonErrors('Les mots de passe de concordent pas.')

    try:
        user.set_password(request.POST['pass1'])
        user.save()
        update_session_auth_hash(request, user)
    except Exception as e:
        return jResponse({'status': 'error',
                          'errors': [str(e)]})

    return jResponse({'status':'ok'})


def requestResetPW(request):
    if request.user.is_authenticated():
        return jsonErrors('Vous devez être déconnecté pour réinitialiser votre mot de passe')
    if 'email' not in request.POST:
        return missingParam('email')

    aspiraUser = User.objects.filter(email=request.POST['email']).first()
    if not aspiraUser:
        return jsonErrors("L'adresse email '%s' n'existe pas."%request.POST['email'])

    aspiraUser.userProfile.passwordResetToken = UserProfile.getUniquePasswordResetToken()
    aspiraUser.userProfile.passwordResetDateLimit = datetime.utcnow()\
        .replace(second=0, microsecond=0, tzinfo=utc) + timedelta(days=1)
    aspiraUser.userProfile.save()

    if DEBUG:
        url = "http://localhost/user/forms/resetPW/"
    else:
        url = "https://aspira.ulaval.ca/user/forms/resetPW/"

    message = render_to_string('AspiraUser/emails/resetPassword.html', {
        'aspiraUser': aspiraUser,
        'link': url+aspiraUser.userProfile.passwordResetToken,
        'webmasters': [user.email for user in User.objects.filter(is_superuser=True, email__isnull=False) if
                       user.email != ''],
    })
    send_mail('SNH - Réinitialisation du mot de passe', 'message',
              'doNotReplyMail', [request.POST['email']], html_message=message)

    return jResponse({'status': 'ok'})


def resetPWPage(request, token):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    profile = UserProfile.objects.filter(passwordResetToken__exact=token).first()
    if not profile:
        raise Http404

    if profile.passwordResetDateLimit < datetime.utcnow().replace(second=0, microsecond=0, tzinfo=utc):
        raise Http404

    if 'pass1' in request.POST and 'pass2' in request.POST:
        return resetPWConfirm(request,profile)


    return render(request,"AspiraUser/reset_pw_page.html",{
        "navigator": [
            ("Réinitialisation du mot de passe", "#"),
        ],
        'token':token,
    })

def resetPWConfirm(request, profile):
    user = profile.user

    if user.check_password(request.POST['pass1']):
        return jsonErrors('Le nouveau mot de passe doit être différent du mot de passe actuel')

    if len(request.POST['pass1']) < 6:
        return jsonErrors('Le mot de passe doit contenir au moins 6 caractères.')

    if request.POST['pass1'] != request.POST['pass2']:
        return jsonErrors('Les mots de passe de concordent pas.')

    try:
        user.set_password(request.POST['pass1'])
        user.save()
        profile.passwordResetToken = None
        profile.passwordResetDateLimit = None
        profile.save()
    except Exception as e:
        return jResponse({'status': 'error',
                          'errors': [str(e)]})

    return jResponse({'status': 'ok'})