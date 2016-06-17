from django.shortcuts import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Twitter.models import *
from Twitter.views import *
from django.db.models import Count, Max, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from AspiraUser.models import UserProfile, TableRowsSelection
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
    twitterUserLimit = aspiraUser.twitterUsersToHarvestLimit
    twitterHashtagLimit = aspiraUser.twitterHashtagToHarvestLimit
    collectedTweets = Tweet.objects.filter(user__harvested_by=aspiraUser).count() # TODO: Add hashtags tweets count
    mostActiveTwitterUser = "None"
    if aspiraUser.twitterUsersToHarvest.count() > 0:
        mostActiveTwitterUser = aspiraUser.twitterUsersToHarvest.annotate(harvested_count=Count('tweets')).order_by("-harvested_count")[0]
    twitterUserPercent = 0
    if twitterUserLimit > 0:
        twitterUserPercent = aspiraUser.twitterUsersToHarvest.count()*100/twitterUserLimit
    twitterHashtagPercent = 0
    if twitterHashtagLimit > 0:
        twitterHashtagPercent = aspiraUser.twitterHashtagsToHarvest.count()*100/twitterHashtagLimit
    mostActiveHashtag = "None"
    if aspiraUser.twitterHashtagsToHarvest.count() > 0:
        mostActiveHashtag = aspiraUser.twitterHashtagsToHarvest.annotate(harvested_count=Count('harvested_tweets')).order_by("-harvested_count")[0].hashtag
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Dashboard", "/"),
        ],
        "twitterUserLimit": twitterUserLimit if twitterUserLimit>0  else "inf",
        "twitterHashtagLimit":twitterHashtagLimit if twitterHashtagLimit>0  else "inf",
        "twitterUserUsage": aspiraUser.twitterUsersToHarvest.count(),
        "twitterUserPercent":twitterUserPercent,
        "twitterHashtagPercent":twitterHashtagPercent,
        "twitterHashtagUsage": aspiraUser.twitterHashtagsToHarvest.count(),
        "collectedTweets": collectedTweets,
        "mostActiveTwitterUser": mostActiveTwitterUser,
        "mostActiveHashtag":mostActiveHashtag,
    })
    request, context = addMessagesToContext(request, context)
    return render_to_response('AspiraUser/dashboard.html', context)


def userLogin(request):
    username = request.POST['username']
    pw = request.POST['password']
    user = authenticate(username=username, password=pw)
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            request.session['aspiraErrors'] = ['This username exists, but the account is inactive. Has the webmaster contacted you back yet?']
    else:
        request.session['aspiraErrors'] = ['Invalid login information']

    return lastUrlOrHome(request)

def userLoginPage(request):
    context = RequestContext(request, {
        'user': request.user,
        'navigator':[
            ('Registration','#')
        ]
    })
    request, context = addMessagesToContext(request, context)
    return render_to_response('AspiraUser/login_page.html', context)


@login_required()
def userLogout(request):
    for select in request.user.tableRowsSelections.all():
        select.delete()
    logout(request)
    return lastUrlOrHome(request)

@login_required()
def userSettings(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Settings", "/settings"),
        ]
    })
    request, context = addMessagesToContext(request, context)
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


def userRegister(request):
    data = request.POST
    aspiraErrors = []
    masterAddrs = [user.email for user in User.objects.filter(is_superuser=True, email__isnull=False) if
                   user.email != '']
    required_fields = {'username':'Username',
                       'email': 'Email address',
                       'pw': 'Password'}
    context = RequestContext(request, {
        'user': request.user,
        'navigator': [
            ('Registration', '#')
        ]
    })

    for field in required_fields.keys():
        if data[field] == '':
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
            'adminAuth': "http://%s/adminauth/user/%s/change/"%(request.get_host(), newUser.pk)
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
            fieldKeeper[field] = data[field]
        context['fieldKeeper'] = fieldKeeper
        template = 'AspiraUser/login_page.html'
    else:
        request.session['aspiraMessages'] = ["Thank you! You will receive an email as soon as your account "+
                                             "is approved by the webmaster."]
        template = 'AspiraUser/register_successful.html'
    request, context = addMessagesToContext(request, context)
    return render_to_response(template, context)



######### TABLE ROWS SELECTION MANAGEMENT ##########

@login_required()
def setUserSelection(request):
    try:
        selection = getUserSelection(request)
        tableId = request.GET['tableId']

        if 'selected' in request.GET:
            selected = request.GET['selected']
            if selected == '_all':
                tableIdsFunctions[tableId](request)
            else:
                queryset = getItemQueryset(selected)
                selection.selectRow(tableId, queryset)

        elif 'unselected' in request.GET:
            unselected = request.GET['unselected']
            if unselected == '_all':
                tableIdsFunctions[tableId](request)
            else:
                queryset = getItemQueryset(unselected)
                selection.unselectRow(tableId, queryset)

        options = [(name[4:],request.GET[name]) for name in request.GET.keys() if 'opt_' in name]
        for option in options:
            selection.setQueryOption(tableId,option[0],option[1])

        return HttpResponse("Done")
    except:
        viewsLogger.exception("AN ERROR OCCURED IN setUserSelection")
        return HttpResponse("An error occured in views")

def getItemFromRowId(rowId):
    className, itemPk = rowId.split('_')
    type = globals()[className]
    return get_object_or_404(type, pk=itemPk)

def getItemQueryset(rowId):
    className, itemPk = rowId.split('__')
    return globals()[className].objects.filter(pk=itemPk)

tableIdsFunctions = {
    'TWTweetTable': TWTweetTableSelection,
    'TWHashtagTable': TWHashtagTableSelection,
    'TWUserTable': TWUserTableSelection,
    'TWUserTweetTable': TWUserTweetTableSelection,
    'TWUserMentionsTable': TWUserMentionsTableSelection,
    'TWFollowersTable': TWFollowersTableSelection,
    'TWFriendsTable': TWFriendsTableSelection,
    'TWUserFavoritesTable': TWUserFavoritesTableSelection,
    'HashtagTweetTable': HashtagTweetTableSelection,
    'TWRetweetTable': TWRetweetTableSelection,
    'TWMentionnedUsersTable': TWMentionnedUsersTableSelection,
    'TWFavoritedByTable': TWFavoritedByTableSelection,
    'TWContainedHashtagsTable': TWContainedHashtagsTableSelection,
    'LinechartTWUserTable': TWUserTableSelection,
}