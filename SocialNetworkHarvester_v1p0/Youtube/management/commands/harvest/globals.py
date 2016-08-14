import threading
import queue
from Youtube.models import YTChannel,YTVideo,YTPlaylist,YTPlaylistItem,YTComment
from AspiraUser.models import UserProfile
from apiclient.discovery import build
from apiclient.errors import HttpError

from SocialNetworkHarvester_v1p0.settings import youtubeLogger, DEBUG
log = lambda s: youtubeLogger.log(s) if DEBUG else 0
pretty = lambda s: youtubeLogger.pretty(s) if DEBUG else 0
logerror = lambda s: youtubeLogger.exception(s)

clientQueue = queue.Queue()