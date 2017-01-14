import threading, re, time
from Youtube.models import YTChannel,YTVideo,YTPlaylist,YTPlaylistItem,YTComment,Subscription
from AspiraUser.models import UserProfile
from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import datetime, timedelta
from django.utils.timezone import utc
from .queues import *
import os
import psutil

from SocialNetworkHarvester_v1p0.settings import youtubeLogger, DEBUG, YOUTUBE_VIDEOS_LOCATION, LOG_DIRECTORY
log = lambda s: youtubeLogger.log(s) if DEBUG else 0
pretty = lambda s: youtubeLogger.pretty(s) if DEBUG else 0
logerror = lambda s: youtubeLogger.exception(s)

global updaterExitFlag
threadsExitFlag = [False]

def today():
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


def xDaysAgo(x=0):
    return today() - timedelta(days=x)


def plurial(i):
    if i > 1:
        return 's'
    else:
        return ''
