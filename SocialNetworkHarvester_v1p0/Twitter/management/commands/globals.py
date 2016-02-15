import threading
import queue
from datetime import datetime
from django.utils.timezone import utc
from Twitter.models import TWUser, friend


from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0

global updaterExitFlag
updaterExitFlag = [False]
updateQueueLock = threading.Lock()
clientQueueLock = threading.Lock()
exceptionQueue = queue.Queue()
exceptionQueueLock = threading.Lock()

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)