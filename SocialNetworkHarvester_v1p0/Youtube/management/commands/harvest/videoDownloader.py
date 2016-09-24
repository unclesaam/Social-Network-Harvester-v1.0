from .commonThread import *
from pytube import YouTube as Ytdwn

class YTVideoDownloader(CommonThread):

    batchSize = 1

    #@youtubeLogger.debug()
    def execute(self):
        videoList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not videosToDownload.empty():
                video = videosToDownload.get()
                videoList.append(video)
                if len(videoList) >= self.batchSize:
                    self.downloadVideo(videoList)
                    log("ytVideos left to download: %s" % videosToDownload.qsize())
                    videoList = []
            elif len(videoList) > 0:
                self.downloadVideo(videoList)
                log("ytvideos left to download: %s" % videosToDownload.qsize())
                videoList = []

    #@youtubeLogger.debug(showArgs=True)
    def downloadVideo(self, videoList):
        ytVideo = videoList[0]
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






