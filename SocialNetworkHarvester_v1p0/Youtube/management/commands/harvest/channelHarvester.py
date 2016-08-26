from .commonThread import *

class YTChannelHarvester(CommonThread):

    batchSize = 1

    #@youtubeLogger.debug()
    def execute(self):
        channelList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not channelHarvestQueue.empty():
                channel = None
                channel = channelHarvestQueue.get()
                channelList.append(channel)
                if len(channelList) >= self.batchSize:
                    self.harvestChannelList(channelList)
                    log("ytChannels left to harvest: %s" % channelHarvestQueue.qsize())
                    channelList = []
            elif len(channelList) > 0:
                self.harvestChannelList(channelList)
                log("ytChannels left to harvest: %s" % channelHarvestQueue.qsize())
                channelList = []

    #@youtubeLogger.debug(showArgs=True)
    def harvestChannelList(self, channelList):
        channel = channelList[0]
        log('Will harvest %s\'s videos'%channel)
        newVidsNumber = 0
        earliestDateHarvested = None
        harvestOverlap = 0
        if not channel._has_reached_begining:
            videos = channel.videos.order_by('-publishedAt')
            if videos:
                earliestDateHarvested = videos[0].publishedAt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        response = self.call(channel,earliestDateHarvested)
        while response and response['items']:
            earliestDateHarvested = response['items'][-1]['snippet']['publishedAt']
            for activity in response['items']:
                if activity['snippet']['type'] == 'upload':
                    id = re.match(r'https://i.ytimg.com/vi/(?P<id>[\w-]+)/default.jpg',
                                  activity['snippet']['thumbnails']['default']['url'])
                    if not id:
                        log('no default thumbnail detected!')
                        pretty(activity)
                        continue
                    video, new = YTVideo.objects.get_or_create(channel=channel,_ident=id.group('id'))
                    if new:
                        video.publishedAt = datetime.strptime(activity['snippet']['publishedAt'],
                                                              '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=utc)
                        video.save()
                        videoToUpdateQueue.put(video)
                        newVidsNumber += 1
                        #log('added a video for %s'%channel)
                        harvestOverlap = 0
                    else:
                        harvestOverlap += 1
                        if channel._has_reached_begining and harvestOverlap > 50:
                            channel._last_video_harvested = today()
                            channel.save()
                            log('%s video-harvest finished. (%i video%s added)' % (channel,
                                    newVidsNumber, plurial(newVidsNumber)))
                            return
            response = self.call(channel, earliestDateHarvested)
            if not response or not response['items']:
                channel._has_reached_begining = True
                channel._last_video_harvested = today()
                channel.save()
                log('%s video-harvest finished. (%i video%s added)'%(channel,
                                            newVidsNumber, plurial(newVidsNumber)))

    def call(self,channel,earliestDate):
        response = None
        client = getClient()
        try:
            response = client.list('activities', channelId=channel._ident,
                           part='snippet', maxResults=50, publishedBefore=earliestDate)
        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                log('%s has returned no results' % channel)
                channel._error_on_harvest = True
                channel.save()
            else:
                returnClient(client)
                raise
        returnClient(client)
        return response