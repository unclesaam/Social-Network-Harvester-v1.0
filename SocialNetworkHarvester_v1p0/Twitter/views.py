from Twitter.ajax import *
from Twitter.tableSelections import *
import csv
from io import TextIOWrapper
import re
from AspiraUser.views import addMessagesToContext

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


@login_required()
def twitterBaseView(request):
    context = {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    }
    request, context = addMessagesToContext(request, context)
    resetUserSelection(request)
    return render(request, 'Twitter/TwitterBase.html', context)


@login_required()
def twUserView(request, TWUser_value):
    queryset = TWUser.objects.filter(screen_name=TWUser_value)
    if not queryset:
        try:
            queryset = TWUser.objects.filter(_ident=TWUser_value)
        except:
            pass
    if not queryset:
        try:
            queryset = TWUser.objects.filter(pk=TWUser_value)
        except:
            pass
    if not queryset:
        raise Http404('No TWUser matches that value')
    twUser = queryset[0]
    context = {
        'user': request.user,
        'twUser':twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/"+TWUser_value),
        ],
    }
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        try:
            return render_to_response('Twitter/TwitterUserSnip.html', context)
        except:
            pass
    else:
        resetUserSelection(request)

        return render(request,'Twitter/TwitterUser.html', context)


@login_required()
def twHashtagView(request, TWHashtagTerm):
    hashtag = get_object_or_404(Hashtag, term=TWHashtagTerm)
    context = {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(hashtag), "#"),
        ],
    }
    resetUserSelection(request)
    return render(request,'Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    tweet = get_object_or_404(Tweet, _ident=tweetId)
    ### TEMPORARY ###
    #tweet = Tweet.objects.annotate(c=Count('replied_by')).order_by('-c')[0]
    log(tweet)
    #################
    twUser = tweet.user
    context = {
        'user': request.user,
        'tweet': tweet,
        'twUser': twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            ((str(twUser) if twUser else 'Unidentifed TWUser'),
             ("/twitter/user/" + (twUser.screen_name or str(twUser._ident)) if twUser else '#')),
            ("Tweet", ""),
        ],
    }
    resetUserSelection(request)
    return render(request,'Twitter/TwitterTweet.html', context)


@login_required()
def addUser(request):
    occuredErrors = []
    userProfile = request.user.userProfile
    screen_names = [sn for sn in request.POST.getlist('screen_name') if sn != '']
    success_count = 0
    log(request.FILES)
    if 'Browse' in request.FILES:
        sns, errors = readScreenNamesFromCSV(request.FILES['Browse'])
        screen_names += sns
        for error in errors:
            occuredErrors.append('An error has occured while parsing your csv file, on line %i.'%error)

    for screen_name in screen_names:
        screen_name = re.sub(',+$', '', screen_name)
        if screenNameIsValid(screen_name):
            twUser, new = TWUser.objects.get_or_create(screen_name=screen_name)
            if userProfile.twitterUsersToHarvest.count() < userProfile.twitterUsersToHarvestLimit:
                userProfile.twitterUsersToHarvest.add(twUser)
                success_count += 1
            else:
                occuredErrors.append('You have reached the maximum number of Twitter users for this Aspira account! (limit: %i)'% userProfile.twitterUsersToHarvestLimit)
                break
        else:
            occuredErrors.append('The user screen name "%s" is invalid. It has been ignored.'% screen_name)

    #request.session['aspiraErrors'] = occuredErrors
    if occuredErrors:
        response = {'status': 'exception', 'errors': occuredErrors}
    else:
        response = {'status': 'ok', 'messages': ['%i Twitter user%s have been added to your list.' % (
            success_count, 's' if success_count > 1 else ''
        )]}
        #request.session['aspiraMessages'] = ['%i Twitter user%s have been added to your list.'%(
        #    success_count, 's' if success_count > 1 else ''
        #)]
    #return HttpResponseRedirect('/twitter')
    return HttpResponse(json.dumps(response), content_type='application/json')

#@viewsLogger.debug(showArgs=True)
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

def screenNameIsValid(screen_name):
    if re.match('^[a-zA-z0-9_]+$', screen_name):
        return True
    return False


@login_required()
def addHashtag(request):
    aspiraErrors = []
    userProfile = request.user.userProfile
    terms = request.POST.getlist('hashtags')
    starts = request.POST.getlist('starts')
    ends = request.POST.getlist('ends')
    hashtags = [(terms[i],starts[i],ends[i]) for i in range(0,len(terms)) if terms[i] != '']
    success_count = 0

    if 'Browse' in request.FILES:
        hs, errors = readHashtagsFromCSV(request.FILES['Browse'])
        hashtags += hs
        for error in errors:
            aspiraErrors.append('An error has occured while parsing your csv file, on line %i.' % error)

    log(hashtags)
    for hashtag in hashtags:
        term = re.sub('(,+$)|#', '', hashtag[0])
        try:
            start = datetime.strptime(hashtag[1], '%m/%d/%Y')
        except ValueError:
            aspiraErrors.append('The start date ("%s") is invalid'% hashtag[1])
            continue
        try:
            end = datetime.strptime(hashtag[2], '%m/%d/%Y')
        except ValueError:
            aspiraErrors.append('The end date ("%s") is invalid' % hashtag[2])
            continue
        if hashtagIsValid(term, start, end):
            twHashtag, new = Hashtag.objects.get_or_create(term=term)
            harvester, new = HashtagHarvester.objects.get_or_create(hashtag=twHashtag, _harvest_since=start,_harvest_until=end)
            if userProfile.twitterHashtagsToHarvest.count() < userProfile.twitterHashtagToHarvestLimit:
                if not userProfile.twitterHashtagsToHarvest.filter(pk=harvester.pk).exists():
                    userProfile.twitterHashtagsToHarvest.add(harvester)
                    success_count += 1
            else:
                aspiraErrors.append(
                    'You have reached the maximum number of Twitter Hashtags for this Aspira account! (limit: %i)' %
                    userProfile.twitterHashtagToHarvestLimit
                )
                break
        else:
            aspiraErrors.append('The Hashtag %s format is invalid. It has been ignored.' % str(hashtag))

    if aspiraErrors:
        response = {'status':'exception','errors' : aspiraErrors}
    else:
        response = {'status': 'ok', 'messages': ['%i new Hashtag%s have been added to your list.' % (
            success_count, 's' if success_count > 1 else '')]}
        #request.session['aspiraMessages'] = ['%i new Hashtag%s have been added to your list.' % (
        #    success_count, 's' if success_count > 1 else ''
        #)]
        #request.session['aspiraErrors'] = aspiraErrors
    #return HttpResponseRedirect('/twitter')
    return HttpResponse(json.dumps(response), content_type='application/json')


def hashtagIsValid(term, start, end):
    log('hashtag: %s, %s-%s'%(term, start, end))
    valid = True
    if not re.match('^#?[a-zA-z0-9_]+$', term):
        valid = False
    if start >= end:
        valid = False
    log('%s'%('valid' if valid else 'invalid'))
    return valid


def readHashtagsFromCSV(file):
    hashtags = []
    errors = []
    rowNum = 0
    for row in file:
        rowNum += 1
        try:
            decodedRow = row.decode('utf8')
            decodedRow = re.sub('[\\r\\n]', '', decodedRow)
            decodedRow = re.sub(',+$', '', decodedRow)
            log(decodedRow)
            if decodedRow != '':
                (term, start, end) = decodedRow.split(',')
                hashtags.append((term, start, end))
        except:
            errors.append(rowNum)
    return hashtags, errors








