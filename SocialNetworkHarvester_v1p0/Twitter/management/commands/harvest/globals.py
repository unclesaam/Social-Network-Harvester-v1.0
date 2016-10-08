import threading
import queue
from datetime import datetime, timedelta
from django.utils.timezone import utc
from Twitter.models import TWUser, follower, favorite_tweet, Tweet, get_from_any_or_create

from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG, LOG_DIRECTORY
log = lambda s : twitterLogger.log(s)
pretty = lambda s : twitterLogger.pretty(s)
logerror = lambda s: twitterLogger.exception(s)

global updaterExitFlag
threadsExitFlag = [False]

updateQueue = queue.Queue()                 #stores twUsers
updateQueue._name = 'updateQueue'
friendsUpdateQueue = queue.Queue()          #stores twUsers
friendsUpdateQueue._name = 'friendsUpdateQueue'
followersUpdateQueue = queue.Queue()        #stores twUsers
followersUpdateQueue._name = 'followersUpdateQueue'
favoriteTweetUpdateQueue = queue.Queue()    #stores twUsers
favoriteTweetUpdateQueue._name = 'favoriteTweetUpdateQueue'
userHarvestQueue = queue.Queue()            #stores twUsers
userHarvestQueue._name = 'userHarvestQueue'

hashtagHarvestQueue = queue.Queue()         #stores twHashtagHarvesters
hashtagHarvestQueue._name = 'hashtagHarvestQueue'

tweetUpdateQueue = queue.Queue()            #stores twTweets
tweetUpdateQueue._name = 'tweetUpdateQueue'
twRetweetUpdateQueue = queue.Queue()        #stores twTweets
twRetweetUpdateQueue._name = 'twRetweetUpdateQueue'

clientQueue = queue.Queue()                 #stores client objects
exceptionQueue = queue.Queue()              #stores exceptions

allQueues = [updateQueue,friendsUpdateQueue,followersUpdateQueue,
             favoriteTweetUpdateQueue,userHarvestQueue,hashtagHarvestQueue,
             tweetUpdateQueue,twRetweetUpdateQueue]

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

def xDaysAgo(x=0):
    return today() - timedelta(days=x)