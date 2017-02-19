import queue

clientQueue = queue.Queue()
exceptionQueue = queue.Queue()

channelUpdateQueue = queue.Queue()
channelUpdateQueue._name = 'channelUpdateQueue'

channelHarvestQueue = queue.Queue()
channelHarvestQueue._name = 'channelHarvestQueue'

videoToUpdateQueue = queue.Queue()
videoToUpdateQueue._name = 'videoToUpdateQueue'

channelToSubsHarvestQueue = queue.Queue()
channelToSubsHarvestQueue._name = 'channelToSubsHarvestQueue'

channelsToCommentHarvestQueue = queue.Queue()
channelsToCommentHarvestQueue._name = 'channelsToCommentHarvestQueue'

commentToUpdateQueue = queue.Queue()
commentToUpdateQueue._name = 'commentToUpdateQueue'

channelsToPlaylistHarvest = queue.Queue()
channelsToPlaylistHarvest._name = "channelsToPlaylistHarvest"

playlistsToUpdate = queue.Queue()
playlistsToUpdate._name = 'playlistsToUpdate'

playlistsToVideoHarvest = queue.Queue()
playlistsToVideoHarvest._name = "playlistsToVideoHarvest"

videosToDownload = queue.Queue()
videosToDownload._name = "videosToDownload"

allQueues = [
    channelUpdateQueue,
    channelHarvestQueue,
    videoToUpdateQueue,
    channelToSubsHarvestQueue,
    channelsToCommentHarvestQueue,
    commentToUpdateQueue,
    channelsToPlaylistHarvest,
    playlistsToVideoHarvest,
    playlistsToUpdate,
    videosToDownload
]