
from AspiraUser.models import UserProfile
from django.contrib.auth.models import User
from .twUserUpdater import *



@twitterLogger.debug()
def harvestTwitter():
    #clearUpdatedTime()
    #resetUpdateErrors()

    all_profiles = UserProfile.objects.filter(twitterApp_parameters_error=False)
    clientList = getClientList(all_profiles)
    clientQueue = queue.Queue()

    clientQueueLock.acquire()
    for client in clientList:
        clientQueue.put(client)
    clientQueueLock.release()

    try:
        launchUpdaterTreads(clientQueue)
    except:
        twitterLogger.exception('An error occured in the twitter harvest routine:')

@twitterLogger.debug()
def launchUpdaterTreads(clientQueue):
    allUserstoUpdate = createUpdateList(TWUser.objects.filter(_error_on_update=False))
    updateQueue = queue.Queue()
    updateThreads = []

    threadNames = ['updater1', 'updater2']#, 'updaterThread3', 'updaterThread4']
    for threadName in threadNames:
        thread = TwUserUpdater(threadName, clientQueue, updateQueue)
        thread.start()
        updateThreads.append(thread)

    updateQueueLock.acquire()
    for user in allUserstoUpdate:
        updateQueue.put(user)
    updateQueueLock.release()

    while not updateQueue.empty():
        if not exceptionQueue.empty():
            exceptionQueueLock.acquire()
            e = exceptionQueue.get()
            exceptionQueueLock.release()
            try:
                raise e
            except:
                twitterLogger.exception('An exception has been retrieved from a Thread.')
                endAllThreads(updateThreads)

    endAllThreads(updateThreads)

@twitterLogger.debug()
def getClientList(profiles):
    clientList = []
    for profile in profiles:
        client = createTwClient(profile)
        if client:
            clientList.append(client)
    return clientList

@twitterLogger.debug()
def createUpdateList(queryset):
    ordered_elements = queryset.filter(_last_updated__isnull=True) | \
                       queryset.filter(_last_updated__lt=today()).order_by('_last_updated')
    #log('ordered_elements: %s'%ordered_elements)
    return ordered_elements

@twitterLogger.debug()
def createTwClient(profile):
    try:
        client = Client(
            ck = profile.twitterApp_consumerKey,
            cs = profile.twitterApp_consumer_secret,
            atk = profile.twitterApp_access_token_key,
            ats = profile.twitterApp_access_token_secret,
        )
        return client
    except tweepy.error.TweepError:
        profile.twitterApp_parameters_error = True
        profile.save()
        log('%s has got an invalid Twitter app'%profile.user)
        return None

@twitterLogger.debug()
def clearUpdatedTime():
    for twUser in TWUser.objects.filter(_last_updated__isnull=False):
        twUser._last_updated = None
        twUser.save()

@twitterLogger.debug()
def resetUpdateErrors():
    for twuser in TWUser.objects.filter(_error_on_update=True):
        twuser._error_on_update = False
        twuser.save()

@twitterLogger.debug()
def endAllThreads(threadList):
    updaterExitFlag[0] = True
    for t in threadList:
        t.join()


class twFriendOflistUpdater(CommonThread):
    pass

class twFollowerlistUpdater(CommonThread):
    pass

class twFollowedlistUpdater(CommonThread):
    pass

class twFavoriteTweetUpdater(CommonThread):
    pass



class twUserHarvester(CommonThread):
    pass

class twHashtagHarvester(CommonThread):
    pass