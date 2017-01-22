from django.shortcuts import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Twitter.models import *
from Twitter.views import *
from Twitter.tableSelections import TWselectBase
from django.db.models import Count, Max, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from .models import UserProfile, TableRowsSelection
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from SocialNetworkHarvester_v1p0.jsonResponses import *
from Youtube.models import *
from Youtube.views.tableSelections import YTselectBase
from django.shortcuts import render
from django.template import Context, Template

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
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
        ]
    }
    request, context = addMessagesToContext(request, context)
    return render(request, 'AspiraUser/settings.html', context)

#@viewsLogger.debug()
@login_required()
def editUserSettings(request):
    user = request.user
    pretty(request.POST)
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
        ]:
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
    return userSettings(request)


def userRegister(request):
    data = request.POST
    aspiraErrors = []
    masterAddrs = [user.email for user in User.objects.filter(is_superuser=True, email__isnull=False) if
                   user.email != '']
    log(masterAddrs)
    required_fields = {'username':'Username',
                       'email': 'Email address',
                       'pw': 'Password'}
    context = {
        'user': request.user,
        'navigator': [
            ('Registration', '#')
        ]
    }

    for field in required_fields.keys():
        if field not in data or data[field] == '':
            aspiraErrors.append('%s is null, please insert a value'% required_fields[field])

    if not aspiraErrors and data['pw'] != data['pw_confirm']:
        aspiraErrors.append('The passwords dont match!')

    if not aspiraErrors and User.objects.filter(email=data['email']).exists():
        aspiraErrors.append('An account with that email already exists!')

    if not aspiraErrors and User.objects.filter(username=data['username']).exists():
        aspiraErrors.append('An account with this username already exists!')

    if not aspiraErrors:
        try:
            validate_email(data['email'])
        except ValidationError:
            aspiraErrors.append('The given email address doesn''t seem valid. Please verify it is correct.')

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



######### TABLE ROWS SELECTION MANAGEMENT ##########

@login_required()
def setUserSelection(request):
    response = {}
    try:
        selection = getUserSelection(request)
        tableId = request.GET['tableId']
        if ('selected' in request.GET and request.GET['selected'] == '_all') or \
            ('unselected' in request.GET and request.GET['unselected'] == '_all'):
            selectUselectAll(request)
        else:
            if 'selected' in request.GET:
                queryset = getItemQueryset(request.GET['selected'])
                selection.selectRow(tableId, queryset)
            elif 'unselected' in request.GET:
                queryset = getItemQueryset(request.GET['unselected'])
                selection.unselectRow(tableId, queryset)
            #else:
            #    raise Exception('"selected" or "unselected" parameter must be present')

        options = [(name[4:], request.GET[name]) for name in request.GET.keys() if 'opt_' in name]
        for option in options:
            selection.setQueryOption(tableId, option[0], option[1])
        response['selectedCount'] = selection.getSelectedRowCount()
        response['status'] = 'completed'
    except:
        viewsLogger.exception("AN ERROR OCCURED IN setUserSelection")
        response = {'status': 'error', 'error': {'description': 'An error occured in views'}}
    return HttpResponse(json.dumps(response), content_type='application/json')

def getItemFromRowId(rowId):
    className, itemPk = rowId.split('_')
    type = globals()[className]
    return get_object_or_404(type, pk=itemPk)

def getItemQueryset(rowId):
    className, itemPk = rowId.split('__')
    return globals()[className].objects.filter(pk=itemPk)

#@viewsLogger.debug(showArgs=True)
def selectUselectAll(request):
    #TODO: fix select_all for tables in tools
    if 'twitter' in request.GET['pageURL'] or 'tool' in request.GET['pageURL']:
        return TWselectBase(request)
    elif 'youtube' in request.GET['pageURL']:
        return YTselectBase(request)
    else:
        raise Exception('Invalid pageURL received')


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




def confAgreement(request):
    return render(request, 'AspiraUser/confidentPol.html',{})