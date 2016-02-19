import threading
import queue
from datetime import datetime
from django.utils.timezone import utc
from Twitter.models import TWUser, friend, follower, favorite_tweet, Tweet


from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0

global updaterExitFlag
threadsExitFlag = [False]

updateQueue = queue.Queue()                 #stores twUsers
updateQueueLock = threading.Lock()

friendsUpdateQueue = queue.Queue()          #stores twUsers
friendsUpdateQueueLock = threading.Lock()

followersUpdateQueue = queue.Queue()        #stores twUsers
followersUpdateQueueLock = threading.Lock()

favoriteTweetUpdateQueue = queue.Queue()    #stores twUsers
favoriteTweetUpdateQueueLock = threading.Lock()

userHarvestQueue = queue.Queue()            #stores twUsers
userHarvestQueueLock = threading.Lock()

hashtagHarvestQueue = queue.Queue()         #stores twHashtags
harvestQueueLock = threading.Lock()

tweetUpdateQueue = queue.Queue()            #stores twTweets
tweetUpdateQueueLock = threading.Lock()

twRetweetUpdateQueue = queue.Queue()            #stores twTweets
twRetweetUpdateQueueLock = threading.Lock()

clientQueue = queue.Queue()                 #stores client objects
clientQueueLock = threading.Lock()

exceptionQueue = queue.Queue()              #stores exceptions
exceptionQueueLock = threading.Lock()

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)
