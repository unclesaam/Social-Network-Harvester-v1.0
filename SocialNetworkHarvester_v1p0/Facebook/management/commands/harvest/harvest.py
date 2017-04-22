
from AspiraUser.models import UserProfile
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_admins, EmailMessage
from django.contrib.auth.models import User
from .fbPageUpdater import *
from django.core.paginator import Paginator

myEmailMessage = [None]
myEmailTitle = [None]
threadList = [[]]

RAMUSAGELIMIT = 600000000 # in bytes
GRAPHRAMUSAGE = False

@facebookLogger.debug()
def harvestFacebook():
    resetFacebookAppError()
    all_profiles = UserProfile.objects.filter(facebookApp_parameters_error=False)
    clientList = getClientList(all_profiles)
    all_profiles = all_profiles.filter(facebookApp_parameters_error=False)
    log('facebookApp_parameters_error profiles: %s'% UserProfile.objects.filter(facebookApp_parameters_error=True))
    if len(all_profiles) == 0 :
        log('No valid Facebook client exists!')
        myEmailTitle[0] = 'Facebook has not launched'
        myEmailMessage[0] = 'No valid Facebook client exists! (reseting them all)'
        for profile in UserProfile.objects.all():
            profile.facebookApp_parameters_error = False
            profile.save()
        return
    clientQueue.maxsize = len(clientList)
    log("clients: %s" % [client.name for client in clientList])
    for client in clientList:
        clientQueue.put(client)


    for thread in [
        (launchFbPagesUpdateThreads, 'launchPagesUpdate', {'profiles': all_profiles}),
        #(launchTweetHarvestThreads, 'launchTweetHarvest', {'profiles': all_profiles}),
        #(launchRetweeterHarvestThreads, 'launchRetweeterHarvest', {'profiles': all_profiles}),
        #(launchTweetUpdateHarvestThread, 'launchTweetUpdateHarvest', {'profiles': all_profiles}),
        #(launchHashagHarvestThreads, 'launchHashagHarvest', {'profiles': all_profiles}),
        #(launchUpdaterTread, 'launchUpdater', {'profiles': all_profiles}),
    ]:
        t = threading.Thread(target=thread[0],name=thread[1],kwargs=thread[2])
        threadList[0].append(t)
        t.start()

    time.sleep(10) # gives some time to the feeder-threads to initialize
    waitForThreadsToEnd()

    if not myEmailTitle[0] and not myEmailMessage[0]:
        myEmailTitle[0] = "Facebook harvest completed"
        myEmailMessage[0] = "Facebook harvest routine has completed successfully"


def resetFacebookAppError():
    for profile in UserProfile.objects.filter(facebookApp_parameters_error=True):
        profile.facebookApp_parameters_error = False
        profile.save()

def send_routine_email(title,message):
    logfilepath = os.path.join(LOG_DIRECTORY, 'facebook.log')
    logfile = open(logfilepath, 'r')
    adresses = [user.email for user in User.objects.filter(is_superuser=True)]
    try:
        email = EmailMessage(title, message)
        email.attachments = [('facebookLogger.log', logfile.read(), 'text/plain')]
        email.to = adresses
        email.from_email = 'Aspira'
        email.send()
        print('%s - Routine email sent to %s'%(datetime.now().strftime('%y-%m-%d_%H:%M'),adresses))
    except Exception as e:
        print('Routine email failed to send')
        print(e)
        facebookLogger.exception('An error occured while sending an email to admin')


#@profile
#@facebookLogger.debug()
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

    put_batch_in_queue(hashtagHarvestQueue, orderQueryset(hashtags, '_last_harvested'))


#@profile
#@facebookLogger.debug()
def launchFbPagesUpdateThreads(*args, **kwargs):
    priorityUpdates = orderQueryset(FBPage.objects.filter(harvested_by__isnull=False, error_on_update=False),
                                       'last_updated', delay=0.5)
    allPagesToUpdate = orderQueryset(FBPage.objects.filter(error_on_update=False)
                                     .exclude(pk__in=priorityUpdates), 'last_updated', delay=5)
    updateThreads = []

    threadNames = ['pageUpdater',]
    for threadName in threadNames:
        thread = FbPageUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    put_batch_in_queue(pageUpdateQueue, priorityUpdates)

    paginator = Paginator(allPagesToUpdate, 1000)
    for page in range(1, paginator.num_pages + 1):
        for page in paginator.page(page).object_list:
            if threadsExitFlag[0]: return
            if QUEUEMAXSIZE == 0 or updateQueue.qsize() < QUEUEMAXSIZE:
                updateQueue.put(page)
            else:
                time.sleep(1)


#@profile
#@facebookLogger.debug()
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

    put_batch_in_queue(userHarvestQueue, twUsers)


#@profile
#@facebookLogger.debug()
def launchNetworkHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = profiles[0].twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)
    for profile in profiles[1:]:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)

    thread1 = TwFriendshipUpdater('friender1')
    threadList[0].append(thread1)
    thread1.start()
    thread2 = TwFollowersUpdater('follower1')
    threadList[0].append(thread2)
    thread2.start()
    thread3 = TwFavTweetUpdater('favtweeter1')
    threadList[0].append(thread3)
    thread3.start()

    put_batch_in_queue(friendsUpdateQueue, orderQueryset(twUsers, '_last_friends_harvested'))
    put_batch_in_queue(followersUpdateQueue, orderQueryset(twUsers, '_last_followers_harvested'))
    put_batch_in_queue(favoriteTweetUpdateQueue, orderQueryset(twUsers, '_last_fav_tweet_harvested'))


#@profile
#@facebookLogger.debug()
def launchRetweeterHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = TWUser.objects.none()
    for profile in profiles:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_network_harvest=False,protected=False)

    tweets = Tweet.objects.none()
    for twUser in twUsers:
        tweets = tweets | twUser.tweets.filter(_error_on_retweet_harvest=False,deleted_at__isnull=True)

    tweets = orderQueryset(tweets, '_last_retweeter_harvested', delay=2)

    threadNames = ['retweeter1','retweeter2']
    for threadName in threadNames:
        thread = TwRetweeterHarvester(threadName)
        threadList[0].append(thread)
        thread.start()

    put_batch_in_queue(twRetweetUpdateQueue, tweets)


#@profile
#@facebookLogger.debug()
def launchTweetUpdateHarvestThread(*args, **kwargs):
    profiles = kwargs['profiles']
    twUsers = profiles[0].twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)
    for profile in profiles[1:]:
        twUsers = twUsers | profile.twitterUsersToHarvest.filter(_error_on_harvest=False,protected=False)

    tweets = twUsers[0].tweets.filter(_error_on_update=False)
    for twUser in twUsers[1:]:
        tweets = tweets | twUser.tweets.filter(_error_on_update=False)

    tweets = orderQueryset(tweets, '_last_updated',delay=2)

    threadNames = ['tweetUpdater1', 'tweetUpdater2']
    for name in threadNames:
        thread = TweetUpdater(name)
        threadList[0].append(thread)
        thread.start()

    put_batch_in_queue(tweetUpdateQueue, tweets)

#@facebookLogger.debug()
def getClientList(profiles):
    clientList = []
    for profile in profiles:
        if not hasattr(profile,'fbAccessToken'):
            profile.facebookApp_parameters_error = True
            profile.save()
        else:
            client = createClient(profile)
            if client:
                clientList.append(client)
    return clientList

#@facebookLogger.debug()
#@profile()
def orderQueryset(queryset, dateTimeFieldName,delay=1):
    isNull = dateTimeFieldName+"__isnull"
    lt = dateTimeFieldName+"__lt"
    ordered_elements = queryset.filter(**{isNull:True}) | \
                       queryset.filter(**{lt: xDaysAgo(delay)}).order_by(dateTimeFieldName)
    return ordered_elements


def put_batch_in_queue(queue, queryset):
    log('preparing to queue %s items in %s'%(queryset.count(), queue._name))
    for item in queryset.iterator():
        if threadsExitFlag[0]: break
        if QUEUEMAXSIZE == 0 or queue.qsize() < QUEUEMAXSIZE:
            queue.put(item)
        else:
            time.sleep(1)
    log('Finished adding %s items in %s'% (queryset.count(),queue._name), showTime=True)

#@facebookLogger.debug()
def clearUpdatedTime():
    for twUser in TWUser.objects.filter(_last_updated__isnull=False):
        twUser._last_updated = None
        twUser.save()

#@facebookLogger.debug()
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

@facebookLogger.debug(showArgs=True)
def resetErrorsTwUser(errorMarker):
    for twuser in TWUser.objects.filter(**{errorMarker:True}):
        setattr(twuser, errorMarker, False)
        twuser.save()


import io, csv, types
@facebookLogger.debug()
def waitForThreadsToEnd():
    notEmptyQueuesNum = -1
    while notEmptyQueuesNum != 0 and not exceptionQueue.qsize():
        time.sleep(3)
        if process.memory_info()[0] >= RAMUSAGELIMIT:
            log('MEMORY USAGE LIMIT EXCEDED!')
            myEmailTitle[0] = 'MEMORY USAGE LIMIT EXCEDED!'
            myEmailMessage[0] = 'Python script memory usage has exceded the set limit (%s Mb)'% \
                                (RAMUSAGELIMIT/1000000)
            queues = allQueues
            return stopAllThreads()
        notEmptyQueues = [(queue._name, queue.qsize()) for queue in allQueues if not queue.empty()]
        if len(notEmptyQueues) != notEmptyQueuesNum and len(notEmptyQueues) <= 20:
            log('Working Queues: %s' % notEmptyQueues)
            notEmptyQueuesNum = len(notEmptyQueues)
    return stopAllThreads()


@facebookLogger.debug()
def stopAllThreads():
    time.sleep(3)
    threadsExitFlag[0] = True
    t = time.time()
    aliveThreads = [thread.name for thread in threadList[0] if thread.isAlive()]
    while len(aliveThreads) > 0 or not exceptionQueue.empty():
        if t + 10 < time.time():
            t = time.time()
            lastAliveThreads = aliveThreads
            aliveThreads = [thread.name for thread in threadList[0] if thread.isAlive()]
            if aliveThreads != lastAliveThreads:
                log('Alive Threads: %s' % aliveThreads)
        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                myEmailMessage[0] = 'An exception has been retrieved from a Thread. (%s)' % threadName
                myEmailTitle[0] = 'SNH - Twitter harvest routine error'
                logerror(myEmailMessage[0])


def cleanDuplicates():
    duplicates = TWUser.objects.filter(_has_duplicate=True)
    if duplicates:
        log("SOME TWUSERS HAVE DUPLICATES!")
        for duplicate in duplicates:
            log("%s has at least a duplicate"%duplicate)
            duplicate._error_on_update = True
            duplicate.save()
    else:
        log('NO DUPLICATE TWUSER FOUND')