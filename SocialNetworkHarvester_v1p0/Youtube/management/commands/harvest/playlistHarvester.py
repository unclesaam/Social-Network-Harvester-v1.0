from .commonThread import *

class YTPlaylistHarvester(CommonThread):

    batchSize = 1
    workQueueName = 'channelsToPlaylistHarvest'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, channelList):
        channel = channelList[0]
        log('Will harvest %s\'s playlists'%channel)
        response = self.call(channel)
        newPlaylistsNum = 0
        while response and response['items']:
            for item in response['items']:
                playlist, new = YTPlaylist.objects.get_or_create(channel=channel,_ident=item['id'])
                if new:
                    newPlaylistsNum += 1
                    playlistsToVideoHarvest.put(playlist)
                    playlistsToUpdate.put(playlist)
                    #log('added a new playlist for %s'%channel)
            if 'nextPageToken' in response:
                response = self.call(channel, token=response['nextPageToken'])
            else:
                response = None
        channel._last_playlists_harvested = today()
        channel.save()
        log('%s playlist-harvest finished. (%i playlists%s added)'%(channel,
                                            newPlaylistsNum, plurial(newPlaylistsNum)))

    def call(self,channel, token=None):
        response = None
        client = getClient()
        try:
            response = client.list('playlists', channelId=channel._ident,
                           part='id', maxResults=50, pageToken=token)
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