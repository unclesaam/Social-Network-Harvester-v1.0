from .globals import *
from .client import Client,getClient,returnClient
from .channelUpdater import YTChannelUpdater
from .channelHarvester import YTChannelHarvester
from .videoUpdater import YTVideoUpdater
from .commentHarvester import YTCommentHarvester
from .commentUpdater import YTCommentUpdater
from .subsHarvester import YTSubscriptionHarvester


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
    threadList += launchCommentHarvestThread(all_profiles) # a channel's comments and all its video's comments
    threadList += launchCommentUpdateThread(all_profiles)
    threadList += launchSubsHarvesterThread(all_profiles)
    time.sleep(2)
    waitForThreadsToEnd(threadList)

@youtubeLogger.debug()
def resetLastUpdated():
    for channel in YTChannel.objects.filter(_last_updated__isnull=False).iterator():
        channel._last_updated = None
        channel.save()
    for vid in YTVideo.objects.filter(_last_updated__isnull=False).iterator():
        vid._last_updated = None
        vid.save()
    for comm in YTComment.objects.filter(_last_updated__isnull=False).iterator():
        comm._last_updated = None
        comm.save()

@youtubeLogger.debug()
def resetLastHarvested():
    for channel in YTChannel.objects.filter(_last_video_harvested__isnull=False).iterator():
        channel._last_video_harvested = None
        channel.save()
    for channel in YTChannel.objects.filter(_last_comment_harvested__isnull=False).iterator():
        channel._last_comment_harvested = None
        channel.save()
    for channel in YTChannel.objects.filter(_last_subs_harvested__isnull=False).iterator():
        channel._last_subs_harvested = None
        channel.save()

@youtubeLogger.debug()
def resetAllErrors():
    pass

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

def orderQueryset(queryset, dateTimeFieldName, delay=0):
    isNull = dateTimeFieldName + "__isnull"
    lt = dateTimeFieldName + "__lt"
    ordered_elements = queryset.filter(**{isNull: True}) | \
                       queryset.filter(**{lt: xDaysAgo(delay)}).order_by(dateTimeFieldName)
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
            break
    return updateThreads

def launchSubsHarvesterThread(profiles):
    '''
    Subs-harvest only the YTUsers that have commented or replied on video-harvested YTUsers.
    TODO: figure the fuck how to select Channels properly.
    https://stackoverflow.com/questions/39157614/generate-a-queryset-from-foreignkey-values
    '''
    return []
    harvestedYTChannels = YTChannel.objects.none()
    for profile in profiles:
        harvestedYTChannels = harvestedYTChannels | profile.ytChannelsToHarvest.filter(_error_on_harvest=False)
    allComments = YTComment.objects.none()
    for channel in harvestedYTChannels:
        allComments = allComments | channel.comments.all()
    l = tuple([comment.pk for comment in allComments])
    allChannelsToSubHarvest = YTChannel.objects.raw("SELECT * FROM snh_2016_schema.youtube_ytchannel "
                                                    "WHERE 'id' IN %s "
                                                    "ORDER BY FIELD('id',%s);"%(l,','.join(map(str, l))))

    for c in allChannelsToSubHarvest:
        log(c)

    allChannelsToSubHarvest = allChannelsToSubHarvest | harvestedYTChannels
    allChannelsToSubHarvest = orderQueryset(allChannelsToSubHarvest.filter(_public_subscriptions=True).distinct(),
                                            '_last_subs_harvested')


    harvestThreads = []
    threadNames = ['subsHarvest1']
    for threadName in threadNames:
        thread = YTSubscriptionHarvester(threadName)
        thread.start()
        harvestThreads.append(thread)

    for channel in allChannelsToSubHarvest.iterator():
        if exceptionQueue.empty():
            channelToSubsHarvestQueue.put(channel)
        else:
            break
    return harvestThreads

def launchCommentUpdateThread(profiles):
    allCommentsToUpdate = orderQueryset(YTComment.objects.filter(_error_on_update=False,
                                                    _deleted_at__isnull=True), '_last_updated')
    updateThreads = []
    threadNames = ['commentUpd1']
    for threadName in threadNames:
        thread = YTCommentUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for comment in allCommentsToUpdate.iterator():
        if exceptionQueue.empty():
            commentToUpdateQueue.put(comment)
        else:
            break
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
            break
    return harvestThreads

def launchVideoUpdateThread(profiles):
    videosToUpdate = orderQueryset(YTVideo.objects.filter(_error_on_update=False), '_last_updated')
    updateThreads = []
    threadNames = ['videoUpdater1','videoUpdater2']
    for threadName in threadNames:
        thread = YTVideoUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for video in videosToUpdate.iterator():
        if exceptionQueue.empty():
            videoToUpdateQueue.put(video)
        else:
            break
    return updateThreads

def launchCommentHarvestThread(profiles):
    channelsToHarvest = YTChannel.objects.none()
    for profile in profiles:
        channelsToHarvest = channelsToHarvest | profile.ytChannelsToHarvest.filter(_error_on_comment_harvest=False)
    channelsToHarvest = orderQueryset(channelsToHarvest.distinct(), '_last_comment_harvested')

    harvestThreads = []
    threadNames = ['commentHarv1']
    for threadName in threadNames:
        thread = YTCommentHarvester(threadName)
        thread.start()
        harvestThreads.append(thread)

    for channel in channelsToHarvest.iterator():
        if exceptionQueue.empty():
            channelsToCommentHarvestQueue.put(channel)
        else:
            break
    return harvestThreads

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
    notEmptyQueuesNum = -1
    t = time.time()
    while notEmptyQueuesNum != 0 and exceptionQueue.empty():
        notEmptyQueues = [queue for queue in workQueues if not queue.empty()]
        if len(notEmptyQueues) != notEmptyQueuesNum:
            log('Not empty queues: %s'%{queue._name:queue.qsize() for queue in notEmptyQueues})
            notEmptyQueuesNum = len(notEmptyQueues)
    return endAllThreads(threadList)


@youtubeLogger.debug()
def endAllThreads(threadList):
    time.sleep(3)
    threadsExitFlag[0] = True
    t = time.time()
    while any([thread.isAlive() for thread in threadList]) or not exceptionQueue.empty():
        if any(not queue.empty() for queue in workQueues) and exceptionQueue.empty():
            return waitForThreadsToEnd(threadList)
        aliveThreads = [thread.name for thread in threadList if thread.isAlive()]

        if t + 5 < time.time():
            t = time.time()
            log('Alive Threads:')
            pretty(aliveThreads)

        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                logerror('An exception has been retrieved from a Thread. (%s)' % threadName)