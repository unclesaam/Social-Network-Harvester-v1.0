from .commonThread import *

class YTVideoUpdater(CommonThread):

    batchSize = 50

    #@youtubeLogger.debug()
    def execute(self):
        videoList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not videoToUpdateQueue.empty():
                video = videoToUpdateQueue.get()
                videoList.append(video)
                if len(videoList) >= self.batchSize:
                    self.updateYTvideoList(videoList)
                    log("ytVideos left to update: %s" % videoToUpdateQueue.qsize())
                    videoList = []
            elif len(videoList) > 0:
                self.updateYTvideoList(videoList)
                log("ytvideos left to update: %s" % videoToUpdateQueue.qsize())
                videoList = []

    #@youtubeLogger.debug(showArgs=True)
    def updateYTvideoList(self, videoList):
        client = getClient()
        try:
            response = client.list('videos', id=",".join([video._ident for video in videoList]),
                part='contentDetails,liveStreamingDetails,localizations,player,recordingDetails,snippet,statistics,status,topicDetails')
        except:
            returnClient(client)
            raise
        returnClient(client)

        for item in response['items']:
            if threadsExitFlag[0]:
                return
            video = next((video for video in videoList if video._ident == item['id']), None)
            if video:
                video.update(item)
                videoList.remove(video)
                video._last_updated = today()
                video.save()
        for video in videoList:
            log( '%s has returned no result' % video)
            video._error_on_update = True
            video.save()