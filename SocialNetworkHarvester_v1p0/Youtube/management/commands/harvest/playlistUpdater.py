from .commonThread import *

class YTPlaylistUpdater(CommonThread):

    batchSize = 50
    workQueueName = 'playlistsToUpdate'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, playlists):
        log('Will update %s playlists'% len(playlists))
        response = self.call(playlists)
        if response and response['items']:
            for item in response['items']:
                playlist = YTPlaylist.objects.get(_ident=item['id'])
                playlist.update(item)
                playlists.remove(playlist)
            for left in playlists:
                left._error_on_update = True
                left.save()

    def call(self, playlists):
        response = None
        client = getClient()
        ids = ''
        try:
            response = client.list('playlists', id=",".join([playlist._ident for playlist in playlists]),
                                   part='snippet,id,status', maxResults=50)
        except Exception as e:
            returnClient(client)
            raise
        returnClient(client)
        return response