from .globals import *
from .client import Client,getClient,returnClient

@youtubeLogger.debug()
def harvestYoutube():
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
    threadList += launchChannelHarvestThreads(all_profiles)
    waitForThreadsToEnd(threadList)


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

def launchChannelHarvestThreads(all_profiles):
    return []

def updateNewChannels():
    client = getClient()
    defaultPart = 'contentDetails,brandingSettings,contentOwnerDetails,id,invideoPromotion,localizations,snippet,statistics,status'
    for channel in YTChannel.objects.filter(_ident__isnull=True):
        response = client.list('channels', forUsername=channel.userName,part=defaultPart)
        data = response['items'][0]

        if YTChannel.objects.filter(_ident=data['id']).exists():
            mergeChannels(channel,YTChannel.objects.get(_ident=data['id']),data)


    allChannelsToUpdate = YTChannel.objects.filter(userName__isnull=True)

@youtubeLogger.debug(showArgs=True)
def mergeChannels(channelA, channelB, data):
    

def waitForThreadsToEnd(allProfiles):
    pass