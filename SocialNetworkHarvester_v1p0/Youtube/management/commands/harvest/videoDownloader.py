from .commonThread import *
from pytube import YouTube as Ytdwn

class YTVideoDownloader(CommonThread):

    batchSize = 1
    workQueueName = 'videosToDownload'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, batch):
        ytVideo = batch[0]
        yt = Ytdwn("http://www.youtube.com/watch?v=%s"%ytVideo._ident)
        filename = 'YT_%s' % ytVideo._ident
        yt.set_filename(filename)
        video = yt.filter(resolution='360p')[0]
        filepath = "%s/%s.%s" % (YOUTUBE_VIDEOS_LOCATION, filename, video.extension)
        if os.path.exists(filepath):
            os.remove(filepath)
        video.download(YOUTUBE_VIDEOS_LOCATION)
        ytVideo._file_path = filepath
        ytVideo.save()






