from .globals import *
from .client import Client,getClient,returnClient
from .channelUpdater import YTChannelUpdater
from .channelHarvester import YTChannelHarvester
from .videoUpdater import YTVideoUpdater
from .commentHarvester import YTCommentHarvester
from .commentUpdater import YTCommentUpdater
from .subsHarvester import YTSubscriptionHarvester
from .playlistHarvester import YTPlaylistHarvester
from .playlistUpdater import YTPlaylistUpdater
from .playlistItemHarvester import YTPlaylistItemHarvester
from .videoDownloader import YTVideoDownloader

myEmailMessage = [None]
myEmailTitle = [None]

threadList = [[]]

RAMUSAGELIMIT = 600000000 # in bytes
GRAPHRAMUSAGE = True

@youtubeLogger.debug()
def harvestYoutube():
    #resetLastUpdated()
    #resetLastHarvested()
    all_profiles = UserProfile.objects.filter(youtubeApp_parameters_error=False)
    clientList = getClientList(all_profiles) # detect errors in apps
    all_profiles = all_profiles.filter(youtubeApp_parameters_error=False) # repetition insures that all apps are valid
    clientQueue.maxsize = len(clientList)
    for client in clientList:
        clientQueue.put(client)

    if clientQueue.empty():
        raise Exception('No Youtube API clients configured')

    if YTChannel.objects.filter(_ident__isnull=True, _error_on_update=False).exists():
        updateNewChannels()

    threadList[0] += launchChannelsUpdateThread(all_profiles)
    threadList[0] += launchChannelsHarvestThread(all_profiles)
    threadList[0] += launchVideoUpdateThread(all_profiles)
    threadList[0] += launchCommentHarvestThread(all_profiles) # a channel's comments and all its video's comments
    threadList[0] += launchCommentUpdateThread(all_profiles)
    threadList[0] += launchSubsHarvesterThread(all_profiles)
    threadList[0] += launchPlaylistsHarvesterThread(all_profiles)
    threadList[0] += launchPlaylistsUpdaterThread(all_profiles)
    threadList[0] += launchPlaylistItemHarvestThread(all_profiles)
    threadList[0] += launchVideoDownloadThread(all_profiles)
    time.sleep(10)
    waitForThreadsToEnd()

    if not myEmailTitle[0] and not myEmailMessage[0]:
        myEmailTitle[0] = "Twitter harvest completed"
        myEmailMessage[0] = "Twitter harvest routine has completed successfully"

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


def send_routine_email(title, message):
    logfilepath = os.path.join(LOG_DIRECTORY, 'youtube.log')
    logfile = open(logfilepath, 'r')
    adresses = [user.email for user in User.objects.filter(is_superuser=True)]
    try:
        email = EmailMessage(title, message)
        email.attachments = [('youtubeLogger.log', logfile.read(), 'text/plain')]
        email.to = adresses
        email.from_email = 'Aspira'
        email.send()
        print('%s - Routine email sent to %s' % (datetime.now().strftime('%y-%m-%d_%H:%M'), adresses))
    except Exception as e:
        print('Routine email failed to send')
        print(e)
        twitterLogger.exception('An error occured while sending an email to admin')

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

def orderQueryset(queryset, dateTimeFieldName, delay=1):
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


def launchPlaylistsUpdaterThread(profiles):
    playlists = orderQueryset(YTPlaylist.objects.filter(_error_on_update=False), '_last_updated', delay=4)
    updateThreads = []

    threadNames = ['playlistUpd1']
    for threadName in threadNames:
        thread = YTPlaylistUpdater(threadName)
        thread.start()
        updateThreads.append(thread)

    for playlist in playlists.iterator():
        if exceptionQueue.empty():
            playlistsToUpdate.put(playlist)
        else:
            break
    return updateThreads

def launchVideoDownloadThread(profiles):
    testVideoDownloadPath()

    videos = YTVideo.objects.filter(_file_path__isnull=True)
    downloadThreads = []

    threadNames = ['vidDwnlder1']
    for threadName in threadNames:
        thread = YTVideoDownloader(threadName)
        thread.start()
        downloadThreads.append(thread)

    for video in videos.iterator():
        if exceptionQueue.empty():
            videosToDownload.put(video)
        else:
            break
    return downloadThreads

def testVideoDownloadPath():
    if not os.path.isdir(YOUTUBE_VIDEOS_LOCATION):
        raise Exception('YOUTUBE_VIDEOS_LOCATION parameter must be an existing folder.')


def launchPlaylistItemHarvestThread(profiles):
    priority_playlists = orderQueryset(YTPlaylist.objects.filter(harvested_by__isnull=False, _error_on_harvest=False), '_last_video_harvested',delay=4)
    playlists = orderQueryset(YTPlaylist.objects.filter(_error_on_harvest=False).exclude(pk__in=priority_playlists), '_last_video_harvested', delay=4)
    harvestThreads = []

    threadNames = ['playItemHarv1']
    for threadName in threadNames:
        thread = YTPlaylistItemHarvester(threadName)
        thread.start()
        harvestThreads.append(thread)

    # prioritize playlists that are directly harvested by users
    for playlist in priority_playlists.iterator():
        if exceptionQueue.empty():
            playlistsToVideoHarvest.put(playlist)
        else:
            break

    for playlist in playlists.iterator():
        if exceptionQueue.empty():
            playlistsToVideoHarvest.put(playlist)
        else:
            break
    return harvestThreads



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


def launchPlaylistsHarvesterThread(profiles):
    channelsToHarvest = YTChannel.objects.none()
    for profile in profiles:
        channelsToHarvest = channelsToHarvest | profile.ytChannelsToHarvest.filter(_error_on_harvest=False)
    channelsToHarvest = orderQueryset(channelsToHarvest.distinct(), '_last_playlists_harvested')

    harvestThreads = []
    threadNames = ['playlistHarv1']
    for threadName in threadNames:
        thread = YTPlaylistHarvester(threadName)
        thread.start()
        harvestThreads.append(thread)

    for channel in channelsToHarvest.iterator():
        if exceptionQueue.empty():
            channelsToPlaylistHarvest.put(channel)
        else:
            break
    return harvestThreads

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


def waitForThreadsToEnd():
    notEmptyQueuesNum = -1
    process = psutil.Process()
    if GRAPHRAMUSAGE:
        csvfile = open(os.path.join(LOG_DIRECTORY, 'youtubeMemLog.csv'), 'w')
        csvfile.write('time,memory usage\n')
        csvfile.close()
    while notEmptyQueuesNum != 0 and not exceptionQueue.qsize():
        time.sleep(3)
        if GRAPHRAMUSAGE:
            csvfile = open(os.path.join(LOG_DIRECTORY, 'youtubeMemLog.csv'), 'a')
            csvfile.write('%s,%s\n' % (time.time(), process.memory_info()[0]))
            csvfile.close()
        if process.memory_info()[0] >= RAMUSAGELIMIT:
            log('MEMORY USAGE LIMIT EXCEDED!')
            myEmailTitle[0] = 'MEMORY USAGE LIMIT EXCEDED!'
            myEmailMessage[0] = 'Python script memory usage has exceded the set limit (%s Mb)' % \
                                (RAMUSAGELIMIT / 1000000)
            queues = workQueues
            return stopAllThreads()
        notEmptyQueues = [(queue._name, queue.qsize()) for queue in workQueues if not queue.empty()]
        if len(notEmptyQueues) != notEmptyQueuesNum and len(notEmptyQueues) <= len(workQueues):
            log('Working Queues: %s' % notEmptyQueues)
            notEmptyQueuesNum = len(notEmptyQueues)
    return stopAllThreads()


@youtubeLogger.debug()
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
                myEmailTitle[0] = 'SNH - Youtube harvest routine error'
                logerror(myEmailMessage[0])
