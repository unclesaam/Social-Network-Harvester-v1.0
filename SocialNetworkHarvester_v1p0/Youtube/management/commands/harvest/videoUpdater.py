from .commonThread import *

class YTVideoUpdater(CommonThread):

    batchSize = 50
    workQueueName = 'videoToUpdateQueue'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, videoList):
        response = self.call()
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

    def call(self):
        client = getClient()
        try:
            response = client.list('videos', id=",".join([video._ident for video in videoList]),
                                   part='contentDetails,liveStreamingDetails,localizations,player,recordingDetails,snippet,statistics,status,topicDetails')
        except:
            returnClient(client)
            raise
        returnClient(client)
        return response

