from .commonThread import *

class YTChannelUpdater(CommonThread):

    batchSize = 50
    workQueueName = 'channelUpdateQueue'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, channelList):
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