import threading
import queue
from datetime import datetime, timedelta
from django.utils.timezone import utc
from Twitter.models import TWUser, follower, favorite_tweet, Tweet


from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0

global updaterExitFlag
threadsExitFlag = [False]

updateQueue = queue.Queue()                 #stores twUsers
friendsUpdateQueue = queue.Queue()          #stores twUsers
followersUpdateQueue = queue.Queue()        #stores twUsers
favoriteTweetUpdateQueue = queue.Queue()    #stores twUsers
userHarvestQueue = queue.Queue()            #stores twUsers

hashtagHarvestQueue = queue.Queue()         #stores twHashtags

tweetUpdateQueue = queue.Queue()            #stores twTweets
twRetweetUpdateQueue = queue.Queue()        #stores twTweets

clientQueue = queue.Queue()                 #stores client objects
exceptionQueue = queue.Queue()              #stores exceptions

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

def xDaysAgo(x=0):
    return today() - timedelta(days=x)