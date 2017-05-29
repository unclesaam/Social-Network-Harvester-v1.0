import threading
import queue
from datetime import datetime, timedelta
from django.utils.timezone import utc
import psutil
import time
from SocialNetworkHarvester_v1p0.settings import facebookLogger
from Facebook.models import FBPage, FBPost, FBComment, FBProfile, FBReaction
#from memory_profiler import profile
import sys
#sys.tracebacklimit = 5

from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG, LOG_DIRECTORY
facebookLogger.reset_log()
def log(*args, **kwargs):
    facebookLogger.log(*args, **kwargs)
pretty = lambda s : facebookLogger.pretty(s)
logerror = lambda s: facebookLogger.exception(s)

process = psutil.Process()

QUEUEMAXSIZE = 0

threadsExitFlag = [False]

class CustomizedQueue(queue.Queue):
    def __init__(self, queueName):
        super().__init__(maxsize=QUEUEMAXSIZE)
        self._name = queueName

pageUpdateQueue = CustomizedQueue('pageUpdateQueue')    #stores FBPages
pageFeedHarvestQueue = CustomizedQueue('pageFeedHarvestQueue')    #stores FBPages
statusUpdateQueue = CustomizedQueue('statusUpdateQueue')    #stores FBPosts
commentUpdateQueue = CustomizedQueue('commentUpdateQueue')    #stores FBComments
profileUpdateQueue = CustomizedQueue('profileUpdateQueue')    #stores FBProfiles
reactionHarvestQueue = CustomizedQueue('reactionHarvestQueue')    #stores FBPosts and FBComments
commentHarvestQueue = CustomizedQueue('commentHarvestQueue')    #stores FBPosts

clientQueue = queue.Queue()                 #stores client objects
exceptionQueue = queue.Queue()              #stores exceptions

allQueues = [pageUpdateQueue, pageFeedHarvestQueue, statusUpdateQueue, reactionHarvestQueue,commentHarvestQueue,
             commentUpdateQueue, profileUpdateQueue]

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

def xDaysAgo(x=0):
    return today() - timedelta(days=x)


startTime = time.time()

def elapsedSeconds():
    return int(time.time() - startTime)