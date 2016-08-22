from .commonThread import *

class YTChannelUpdater(CommonThread):

    batchSize = 50

    #@youtubeLogger.debug()
    def execute(self):
        channelList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not channelUpdateQueue.empty():
                channel = channelUpdateQueue.get()
                channelList.append(channel)
                if len(channelList) >= self.batchSize:
                    self.updateYTChannelList(channelList)
                    log("ytChannels left to update: %s" % channelUpdateQueue.qsize())
                    channelList = []
            elif len(channelList) > 0:
                self.updateYTChannelList(channelList)
                log("ytChannels left to update: %s" % channelUpdateQueue.qsize())
                channelList = []

    #@youtubeLogger.debug(showArgs=True)
    def updateYTChannelList(self, channelList):
        client = getClient()
        response = client.list('channels', id=",".join([channel._ident for channel in channelList]),
            part='brandingSettings,contentOwnerDetails,id,invideoPromotion,localizations,snippet,statistics,status')
        returnClient(client)

        for item in response['items']:
            if threadsExitFlag[0]:
                return
            channel = next((channel for channel in channelList if channel._ident == item['id']), None)
            if channel:
                channel.update(item)
                channelList.remove(channel)
                channel._last_updated = today()
                channel.save()
        for channel in channelList:
            log( '%s has returned no result' % channel)
            channel._error_on_update = True
            channel.save()