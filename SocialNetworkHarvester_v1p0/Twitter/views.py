from Twitter.ajax import *
import csv
from io import TextIOWrapper
import re

@login_required()
def twitterBaseView(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    })
    if hasattr(request, 'aspiraErrors'):
        context['aspiraErrors'] = request.aspiraErrors
    return render_to_response('Twitter/TwitterBase.html', context)

def twUserView(request, TWUser_value):

    twUser = TWUser.objects.filter(screen_name=TWUser_value)
    if not twUser:
        try:
            twUser = TWUser.objects.filter(_ident=TWUser_value)
        except:
            pass
    if not twUser:
        try:
            twUser = TWUser.objects.filter(pk=TWUser_value)
        except:
            pass
    if not twUser:
        raise Http404('No TWUser matches that value')
    twUser = twUser[0]
    context = RequestContext(request, {
        'user': request.user,
        'twUser':twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/"+TWUser_value),
        ],
    })
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        return render_to_response('Twitter/TwitterUserSnip.html', context)
    else:
        return render_to_response('Twitter/TwitterUser.html', context)

def twHashtagView(request, TWHashtagTerm):
    hashtag = get_object_or_404(Hashtag, term=TWHashtagTerm)
    context = RequestContext(request, {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(hashtag), "#"),
        ],
    })
    return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    tweet = get_object_or_404(Tweet, _ident=tweetId)
    twUser = tweet.user
    context = RequestContext(request, {
        'user': request.user,
        'tweet': tweet,
        'twUser': twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/" + (twUser.screen_name or str(twUser._ident))),
            ("Tweet", ""),
        ],
    })
    return render_to_response('Twitter/TwitterTweet.html', context)


@login_required()
def addUser(request):
    occuredErrors = []
    userProfile = request.user.userProfile
    screen_names = [sn for sn in request.POST.getlist('screen_name') if sn != '']
    if 'Browse' in request.FILES:
        sns, errors = readScreenNamesFromCSV(request.FILES['Browse'])
        screen_names += sns
        for error in errors:
            occuredErrors.append('An error has occured while parsing your csv file, on line %i.'%error)

    for screen_name in screen_names:
        screen_name = re.sub(',+$', '', screen_name)
        if isValid(screen_name):
            twUser, new = TWUser.objects.get_or_create(screen_name=screen_name)
            if userProfile.twitterUsersToHarvest.count() < userProfile.twitterUsersToHarvestLimit:
                userProfile.twitterUsersToHarvest.add(twUser)
        else:
            occuredErrors.append('The user screen name "%s" is invalid. It has been ignored.'% screen_name)

    request.aspiraErrors = occuredErrors
    return twitterBaseView(request)


def readScreenNamesFromCSV(file):
    screen_names = []
    errors = []
    rowNum = 0
    for row in file:
        rowNum += 1
        try:
            decodedRow = row.decode('utf8')
            decodedRow = re.sub('[\\r\\n]', '', decodedRow)
            screen_names.append(decodedRow)
        except UnicodeDecodeError:
            #log('an invalid line was retrieved')
            errors.append(rowNum)
    return screen_names, errors

def isValid(screen_name):
    log('screen_name: '+ screen_name)
    if re.match('^[\w_]+$', screen_name):
        log('valid')
        return True
    log('invalid')
    return False