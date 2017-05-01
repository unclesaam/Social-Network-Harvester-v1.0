import threading
import queue
from datetime import datetime, timedelta
from django.utils.timezone import utc
import psutil
import time
from SocialNetworkHarvester_v1p0.settings import facebookLogger
from Facebook.models import FBPage, FBPost, FBComment, FBProfile
#from memory_profiler import profile

from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG, LOG_DIRECTORY
def log(*args, **kwargs):
    facebookLogger.log(*args, **kwargs)
pretty = lambda s : facebookLogger.pretty(s)
logerror = lambda s: facebookLogger.exception(s)

process = psutil.Process()

QUEUEMAXSIZE = 10000

threadsExitFlag = [False]

pageUpdateQueue = queue.Queue(maxsize=QUEUEMAXSIZE)    #stores FBPages
pageUpdateQueue._name = 'pageUpdateQueue'
pageFeedHarvestQueue = queue.Queue(maxsize=QUEUEMAXSIZE)  # stores FBPages
pageFeedHarvestQueue._name = "pageFeedHarvestQueue"
statusUpdateQueue = queue.Queue(maxsize=QUEUEMAXSIZE)  # stores FBPosts
statusUpdateQueue._name = "statusUpdateQueue"
profileUpdateQueue = queue.Queue(maxsize=QUEUEMAXSIZE)  # stores FBProfiles
profileUpdateQueue._name = "profileUpdateQueue"


clientQueue = queue.Queue()                 #stores client objects
exceptionQueue = queue.Queue()              #stores exceptions

allQueues = [pageUpdateQueue, pageFeedHarvestQueue, statusUpdateQueue]

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

def xDaysAgo(x=0):
    return today() - timedelta(days=x)


startTime = time.time()

def elapsedSeconds():
    return int(time.time() - startTime)