from .commonThread import *

class YTPlaylistItemHarvester(CommonThread):

    batchSize = 1
    workQueueName = 'playlistsToVideoHarvest'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, playlists):
        playlist = playlists[0]
        log('Will harvest %s\'s videos'%playlist)
        response = self.call(playlist)
        while response and response['items']:
            for item in response['items']:
                videoId = item['snippet']['resourceId']['videoId']
                if YTVideo.objects.filter(_ident=videoId).exists():
                    video = YTVideo.objects.get(_ident=videoId)
                else:
                    channelId = item['snippet']['channelId']
                    channel, new = YTChannel.objects.get_or_create(_ident=channelId)
                    if new:
                        channelUpdateQueue.put(channel)
                    video = YTVideo.objects.create(_ident=videoId,channel=channel)
                    videoToUpdateQueue.put(video)
                    videosToDownload.put(video)
                playlistItem, new = YTPlaylistItem.objects.get_or_create(playlist=playlist,video=video)
                playlistItem.playlistOrder = item['snippet']['position']
                playlistItem.save()

            if 'nextPageToken' in response:
                response = self.call(playlist, token=response['nextPageToken'])
            else:
                response = None
                playlist._last_video_harvested = today()
                playlist.save()
                log('%s video-harvest finished.' % playlist)


    def call(self,playlist,token=None):
        response = None
        client = getClient()
        try:
            response = client.list('playlistItems', playlistId=playlist._ident,
                           part='snippet', maxResults=50, pageToken=token)
        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                log('%s has returned no results' % playlist)
                playlist._error_on_harvest = True
                playlist.save()
            else:
                returnClient(client)
                raise
        returnClient(client)
        return response