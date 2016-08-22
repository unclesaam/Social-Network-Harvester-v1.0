from .globals import *
from .client import Client,getClient,returnClient
from .channelUpdater import YTChannelUpdater
from .channelHarvester import YTChannelHarvester
from .videoUpdater import YTVideoUpdater


@youtubeLogger.debug()
def harvestYoutube():
    resetLastUpdated()
    resetLastHarvested()
    all_profiles = UserProfile.objects.filter(youtubeApp_parameters_error=False)
    clientList = getClientList(all_profiles)
    all_profiles = all_profiles.filter(youtubeApp_parameters_error=False) # repetition insures that all apps are valid
    clientQueue.maxsize = len(clientList)
    for client in clientList:
        clientQueue.put(client)

    if clientQueue.empty():
        raise Exception('No Youtube API clients configured')

    if YTChannel.objects.filter(_ident__isnull=True, _error_on_update=False).exists():
        updateNewChannels()

    threadList = []
    threadList += launchChannelsUpdateThread(all_profiles)
    threadList += launchChannelsHarvestThread(all_profiles)
    threadList += launchVideoUpdateThread(all_profiles)
    time.sleep(2)
    waitForThreadsToEnd(threadList)

def resetLastUpdated():
    for channel in YTChannel.objects.filter(_last_updated__isnull=False).iterator():
        channel._last_updated = None
        channel.save()
    for vid in YTVideo.objects.filter(_last_updated__isnull=False).iterator():
        vid._last_updated = None
        vid.save()

def resetLastHarvested():
    for channel in YTChannel.objects.filter(_last_video_harvested__isnull=False).iterator():
        channel._last_video_harvested = None
        channel.save()

def getClientList(profiles):
    clientList = []
    for profile in profiles:
        client = createYTClient(profile)
        if client:
            clientList.append(client)
    return clientList

def createYTClient(profile):
    try:
        client = Client(profile.youtubeApp_dev_key)
        return client
    except:
        profile.youtubeApp_parameters_error = True
        profile.save()
        return None

def orderQueryset(queryset, dateTimeFieldName):
    isNull = dateTimeFieldName + "__isnull"
    lt = dateTimeFieldName + "__lt"
    ordered_elements = queryset.filter(**{isNull: True}) | \
                       queryset.filter(**{lt: today()}).order_by(dateTimeFieldName)
    return ordered_elements

def launchChannelsUpdateThread(all_profiles):
    allChannelsToUpdate = orderQueryset(YTChannel.objects.filter(_error_on_update=False), '_last_updated')
    updateThreads = []

    threadNames = ['channUpd1']
    for threadName in threadNames:
        thread = YTChannelUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for channel in allChannelsToUpdate.iterator():
        if exceptionQueue.empty():
            channelUpdateQueue.put(channel)
        else:
            return updateThreads
    return updateThreads

def launchChannelsHarvestThread(profiles):
    channelsToHarvest = YTChannel.objects.none()
    for profile in profiles:
        channelsToHarvest = channelsToHarvest | profile.ytChannelsToHarvest.filter(_error_on_harvest=False)
    channelsToHarvest = orderQueryset(channelsToHarvest.distinct(), '_last_video_harvested')
    harvestThreads = []

    threadNames = ['chanHarv1']
    for threadName in threadNames:
        thread = YTChannelHarvester(threadName)
        thread.start()
        harvestThreads.append(thread)

    for channel in channelsToHarvest.iterator():
        if exceptionQueue.empty():
            channelHarvestQueue.put(channel)
        else:
            return harvestThreads
    return harvestThreads

def launchVideoUpdateThread(profiles):
    videosToUpdate = orderQueryset(YTVideo.objects.filter(_error_on_update=False), '_last_updated')
    updateThreads = []
    threadNames = ['videoUpdater1']
    for threadName in threadNames:
        thread = YTVideoUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for video in videosToUpdate.iterator():
        if exceptionQueue.empty():
            videoToUpdateQueue.put(video)
        else:
            return updateThreads
    return updateThreads

def updateNewChannels(): #only channels that dont have a channelId but have a userName value.
    client = getClient()
    defaultPart = 'contentDetails,brandingSettings,contentOwnerDetails,id,invideoPromotion,localizations,snippet,statistics,status'
    for channel in YTChannel.objects.filter(_ident__isnull=True):
        response = client.list('channels', forUsername=channel.userName,part=defaultPart)
        data = response['items'][0]
        if YTChannel.objects.filter(_ident=data['id']).exists():
            idChannel = YTChannel.objects.get(_ident=data['id'])
            idChannel.userName = channel.userName
            idChannel.update(data)
            channel.delete()
        else:
            channel.update(data)

@youtubeLogger.debug()
def waitForThreadsToEnd(threadList):
    while 1:
        if all([queue.empty() for queue in workQueues]):
            log("all lists are empty, terminating all threads")
            break
        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                logerror('An exception has been retrieved from a Thread. (%s)' % threadName)
                break
    endAllThreads(threadList)


@youtubeLogger.debug()
def endAllThreads(threadList):
    time.sleep(3)
    threadsExitFlag[0] = True
    aliveThreadsCount = 0
    while any([thread.isAlive() for thread in threadList]) or not exceptionQueue.empty():

        aliveThreads = [thread.name for thread in threadList if thread.isAlive()]
        if len(aliveThreads) != aliveThreadsCount:
            log('Alive Threads: %s'% aliveThreads)
            aliveThreadsCount = len(aliveThreads)

        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                logerror('An exception has been retrieved from a Thread. (%s)' % threadName)