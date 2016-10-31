
from AspiraUser.models import UserProfile
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_admins, EmailMessage
from django.contrib.auth.models import User
from .twUserUpdater import *
from .twFriendshipUpdater import *
from .twFollowersUpdater import *
from .twFavTweetUpdater import *
from .twUserHarvester import *
from .twRetweeterHarvester import *
from .tweetUpdater import *
from .twHashtagHarvester import *

myEmailMessage = [None]
myEmailTitle = [None]
threadList = [[]]

@twitterLogger.debug()
def harvestTwitter():
    #resetErrorsTwUser("_error_on_network_harvest")
    #resetErrorsTwUser("_error_on_update")
    #clearNetworkHarvestTime()
    all_profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
    clientList = getClientList(all_profiles)
    all_profiles = all_profiles.filter(twitterApp_parameters_error=False) # insures that his/her twitter app is valid
    log('twitterApp_parameters_error profiles: %s'% UserProfile.objects.filter(twitterApp_parameters_error=True))
    if len(all_profiles) == 0:
        log('No valid Twitter client exists!')
        return
    clientQueue.maxsize = len(clientList)
    for client in clientList:
        clientQueue.put(client)

    if TWUser.objects.filter(_ident__isnull=True, _error_on_update=False).exists():
        updateNewUsers(all_profiles)

    for thread in [
        launchNetworkHarvestThreads,
        launchTweetHarvestThreads,
        launchRetweeterHarvestThreads,
        launchTweetUpdateHarvestThread,
        launchHashagHarvestThreads,
        launchUpdaterTread,
    ]:
        threading.Thread(target=thread,kwargs={'profiles':all_profiles}).start()

    time.sleep(10)
    waitForThreadsToEnd()

    if not myEmailTitle[0] and not myEmailMessage[0]:
        myEmailTitle[0] = "Twitter harvest completed"
        myEmailMessage[0] = "Twitter harvest routine has completed successfully"


def send_routine_email(title,message):
    logfilepath = os.path.join(LOG_DIRECTORY, 'twitter.log')
    logfile = open(logfilepath, 'r')
    adresses = [user.email for user in User.objects.filter(is_superuser=True)]
    try:
        email = EmailMessage(title, message)
        email.attachments = [('twitterlogger.log', logfile.read(), 'text/plain')]
        email.to = adresses
        email.from_email = 'Aspira'
        email.send()
        print('%s - Routine email sent to %s'%(datetime.datetime.now().strftime('%y-%m-%d_%H:%M'),adresses))
    except Exception as e:
        print('Routine email failed to send')
        print(e)
        twitterLogger.exception('An error occured while sending an email to admin')


@twitterLogger.debug(showArgs=True)
def updateNewUsers(all_profiles):
    allNewUsers = list(TWUser.objects.filter(_ident__isnull=True, _error_on_update=False))
    userlists = [allNewUsers[i:i+100] for i in range(0,len(allNewUsers), 100)]
    log("userlists: %s"% userlists)
    for userList in userlists:
        client = getClient('lookup_users')
        try:
            responses = client.call('lookup_users', screen_names=[user.screen_name for user in userList])
        except tweepy.error.TweepError as e: #None of the usernames exists
            for falseUser in userList:
                log('%s has returned no result' % falseUser)
                falseUser._error_on_update = True
                falseUser.save()
        returnClient(client)
    for response in responses:
        user = next((user for user in allNewUsers if user.screen_name == response._json['screen_name']), None)
        log('user: %s'%user)
        if user:
            user.UpdateFromResponse(response._json)
            allNewUsers.remove(user)
    for user in allNewUsers:
        log('%s has returned no result' % user)
        user._error_on_update = True
        user.save()

@twitterLogger.debug()
def launchHashagHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    hashtags = profiles[0].twitterHashtagsToHarvest.all()
    for profile in profiles[1:]:
        hashtags = hashtags | profile.twitterHashtagsToHarvest.all()

    harvestThread = []
    threadNames = ['hashtager1']
    for threadName in threadNames:
        thread = TwHashtagHarvester(threadName)
        thread.start()
        harvestThread.append(thread)

    for hashtag in orderQueryset(hashtags, '_last_harvested'):
        if exceptionQueue.empty():
            hashtagHarvestQueue.put(hashtag)
        else:
            break
    log("hashtagHarvestQueue contains %s items"% hashtagHarvestQueue.qsize())
    return harvestThread

@twitterLogger.debug()
def launchUpdaterTread(*args, **kwargs):
    priority_updates = orderQueryset(TWUser.objects.filter(harvested_by__isnull=False, _error_on_update=False),
                                       '_last_updated', delay=0.5)
    allUserstoUpdate = orderQueryset(TWUser.objects.filter(_error_on_update=False)
                                     .exclude(pk__in=priority_updates), '_last_updated', delay=3)
    updateThreads = []

    threadNames = ['userUpdater1','userUpdater2','userUpdater3']
    for threadName in threadNames:
        thread = TwUserUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for user in priority_updates.iterator():
        if exceptionQueue.empty():
            updateQueue.put(user)
        else:
            break
    for user in allUserstoUpdate.iterator():
        if exceptionQueue.empty():
            updateQueue.put(user)
        else:
            break
    return updateThreads

@twitterLogger.debug()
def launchTweetHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = profiles[0].twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)
    for profile in profiles[1:]:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)

    twUsers = orderQueryset(twUsers, '_last_tweet_harvested', delay=1)


    threadNames = ['harvester1']
    for threadName in threadNames:
        thread = TwUserHarvester(threadName)
        thread.start()
        threadList[0].append(thread)

    for twUser in twUsers:
        userHarvestQueue.put(twUser)

def launchNetworkHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = profiles[0].twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)
    for profile in profiles[1:]:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)

    for twUser in orderQueryset(twUsers, '_last_friends_harvested'):
        friendsUpdateQueue.put(twUser)
    #log("friendsUpdateQueue contains %s elements"% friendsUpdateQueue.qsize())

    for twUser in orderQueryset(twUsers, '_last_followers_harvested'):
        followersUpdateQueue.put(twUser)
    #log("followersUpdateQueue contains %s elements" % followersUpdateQueue.qsize())

    for twUser in orderQueryset(twUsers, '_last_fav_tweet_harvested'):
        favoriteTweetUpdateQueue.put(twUser)
    #log("favoriteTweetUpdateQueue contains %s elements" % favoriteTweetUpdateQueue.qsize())

    thread = TwFriendshipUpdater('friender1')
    thread.start()
    threadList[0].append(thread)
    thread = TwFollowersUpdater('follower1')
    thread.start()
    threadList[0].append(thread)
    thread = TwFavTweetUpdater('favtweeter1')
    thread.start()
    threadList[0].append(thread)


def launchRetweeterHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = TWUser.objects.none()
    for profile in profiles:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)

    tweets = Tweet.objects.none()
    for twUser in twUsers:
        tweets = tweets | twUser.tweets.filter(_error_on_retweet_harvest=False,deleted_at__isnull=True)

    tweets = orderQueryset(tweets, '_last_retweeter_harvested')

    threadNames = ['retweeter1','retweeter2']
    for threadName in threadNames:
        thread = TwRetweeterHarvester(threadName)
        thread.start()
        threadList[0].append(thread)

    for tweet in tweets.iterator():
        if exceptionQueue.empty():
            twRetweetUpdateQueue.put(tweet)

def launchTweetUpdateHarvestThread(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = profiles[0].twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)
    for profile in profiles[1:]:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)

    tweets = twUsers[0].tweets.filter(_error_on_update=False)
    for twUser in twUsers[1:]:
        tweets = tweets | twUser.tweets.filter(_error_on_update=False)

    tweets = orderQueryset(tweets, '_last_updated')

    thread = TweetUpdater('tweetUpdater1')
    thread.start()
    threadList[0].append(thread)

    for tweet in tweets.iterator():
        if exceptionQueue.empty():
            tweetUpdateQueue.put(tweet)

#@twitterLogger.debug()
def getClientList(profiles):
    clientList = []
    for profile in profiles:
        client = createTwClient(profile)
        if client:
            clientList.append(client)
    return clientList

#@twitterLogger.debug()
def orderQueryset(queryset, dateTimeFieldName,delay=1):
    isNull = dateTimeFieldName+"__isnull"
    lt = dateTimeFieldName+"__lt"
    ordered_elements = queryset.filter(**{isNull:True}) | \
                       queryset.filter(**{lt: xDaysAgo(delay)}).order_by(dateTimeFieldName)
    return ordered_elements

#@twitterLogger.debug()
def createTwClient(profile):
    try:
        client = Client(
            name = "%s's App"%profile.user,
            ck = profile.twitterApp_consumerKey,
            cs = profile.twitterApp_consumer_secret,
            atk = profile.twitterApp_access_token_key,
            ats = profile.twitterApp_access_token_secret,
        )
        return client
    except tweepy.error.TweepError:
        profile.twitterApp_parameters_error = True
        profile.save()
        twitterLogger.exception('%s has got an invalid Twitter app'%profile.user)
        return None

@twitterLogger.debug()
def clearUpdatedTime():
    for twUser in TWUser.objects.filter(_last_updated__isnull=False):
        twUser._last_updated = None
        twUser.save()

@twitterLogger.debug()
def clearNetworkHarvestTime():
    for twUser in TWUser.objects.filter(_last_friends_harvested__isnull=False):
        twUser._last_friends_harvested = None
        twUser.save()
    for twUser in TWUser.objects.filter(_last_followers_harvested__isnull=False):
        twUser._last_followers_harvested = None
        twUser.save()
    for twUser in TWUser.objects.filter(_last_fav_tweet_harvested__isnull=False):
        twUser._last_fav_tweet_harvested = None
        twUser.save()

@twitterLogger.debug(showArgs=True)
def resetErrorsTwUser(errorMarker):
    for twuser in TWUser.objects.filter(**{errorMarker:True}):
        setattr(twuser, errorMarker, False)
        twuser.save()



@twitterLogger.debug()
def waitForThreadsToEnd():
    notEmptyQueuesNum = -1
    t = time.time()
    while notEmptyQueuesNum != 0 and exceptionQueue.empty() and not threadsExitFlag[0]:
        notEmptyQueues = [queue for queue in allQueues if not queue.empty()]
        if len(notEmptyQueues) != notEmptyQueuesNum and len(notEmptyQueues) <= 3:
            log('Working Queues: %s' % {queue._name: queue.qsize() for queue in notEmptyQueues})
            notEmptyQueuesNum = len(notEmptyQueues)
    return endAllThreads()

@twitterLogger.debug()
def endAllThreads():
    time.sleep(3)
    threadsExitFlag[0] = True
    t = time.time()
    while any([thread.isAlive() for thread in threadList[0]]) or not exceptionQueue.empty():
        aliveThreads = [thread.name for thread in threadList[0] if thread.isAlive()]

        if t + 10 < time.time():
            t = time.time()
            log('Alive Threads: %s' % aliveThreads)

        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                myEmailMessage[0] = 'An exception has been retrieved from a Thread. (%s)' % threadName
                myEmailTitle[0] = 'SNH - Twitter harvest routine error'
                logerror(myEmailMessage[0])
