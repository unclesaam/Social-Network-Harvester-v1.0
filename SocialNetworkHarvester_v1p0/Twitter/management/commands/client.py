import re
from sys import maxsize as MAX_INT
import time
from .globals import *
import tweepy

class Client:

    #refreshTimer = MAX_INT
    callsMap = {
        #'callName' : 'callIdentifier',
        'lookup_users': '/users/lookup',
        'friends_ids': '/friends/ids',
        'rate_limit_status': '/application/rate_limit_status',
        'followers_ids': '/followers/ids',
        'favorites': '/favorites/list',
        'user_timeline': '/statuses/user_timeline',
    }

    def __str__(self):
        return self.name

    #@twitterLogger.debug()
    def __init__(self, **kwargs):
        ck = kwargs['ck']
        cs = kwargs['cs']
        atk = kwargs['atk']
        ats = kwargs['ats']
        auth = tweepy.OAuthHandler(ck, cs)
        auth.set_access_token(atk, ats)
        self.api = tweepy.API(auth)
        self.refreshLimits()
        self.name = kwargs['name'] if "name" in kwargs else "Unnamed client"

    @twitterLogger.debug()
    def call(self, callName, *args, **kwargs):
        if time.time() >= self.getResetTime(callName):
            self.refreshLimits()
        remainingCalls = self.getRemainingCalls(callName)
        if remainingCalls > 0:
            self.setRemainingCalls(callName, remainingCalls-1)
            try:
                return getattr(self.api, callName)(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                time.sleep(2)
                return call(callName, *args, **kwargs)
        else:
            raise Exception('No more calls of type "%s"'%self.callsMap[callName])

    @twitterLogger.debug()
    def refreshLimits(self):
        response = self.api.rate_limit_status()
        #pretty(response)
        self.limits = response['resources']

    #@twitterLogger.debug()
    def getRemainingCalls(self, callName):
        callIdentifier = self.callsMap[callName]
        return self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['remaining']

    #@twitterLogger.debug()
    def setRemainingCalls(self, callName, value):
        callIdentifier = self.callsMap[callName]
        self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['remaining'] = value

    #@twitterLogger.debug()
    def getResetTime(self, callName):
        callIdentifier = self.callsMap[callName]
        #log('item found: %s'%re.search(r'(?<=/)\w+(?=/)', callIdentifier))
        return self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['reset']


@twitterLogger.debug()
def getClient(callName):
    client = None
    clientQueueLock.acquire()
    if not clientQueue.empty():
        client = clientQueue.get()
    clientQueueLock.release()
    while not client or client.getRemainingCalls(callName) <= 0 :
        clientQueueLock.acquire()
        if client:
            #log('got %s. Remaining %s calls: %i'%(client, callName, client.getRemainingCalls(callName)))
            clientQueue.put(client)
        elif not clientQueue.empty():
            client = clientQueue.get()
        clientQueueLock.release()
    log('Client found: %s. Remaining "%s" calls: %s'%(client.name, callName, client.getRemainingCalls(callName)))
    #log('%i Clients available'%clientQueue.qsize())
    return client

@twitterLogger.debug()
def returnClient(client):
    if clientQueue.full():
        raise Exception("Client Queue is already full. There is a Client that is returned twice!")
    clientQueueLock.acquire()
    clientQueue.put(client)
    clientQueueLock.release()
    #log("Returned %s"%client)
    #log('%s Clients available'%clientQueue.qsize())


class CursorWrapper:

    def __init__(self, callName, **kwargs):
        self.callName = callName
        self.client = getClient(self.callName)
        self.cursor = tweepy.Cursor(getattr(self.client.api, self.callName), **kwargs).items()
        self.kwargs = kwargs

    #@twitterLogger.debug()
    def next(self):
        try:
            return self.cursor.next()
        except tweepy.error.RateLimitError:
            twitterLogger.exception('RateLimitError caught!')
            nextCursor = self.cursor.page_iterator.next_cursor
            self.client.setRemainingCalls(callName, 0)
            returnClient(self.client)
            self.client = getClient(self.callName)
            self.cursor = tweepy.Cursor(self.client.api.friends_ids, cursor=nextCursor, **self.kwargs).items()
            return self.next()

        except StopIteration:
            self.end()
            return None

        except tweepy.error.TweepError as e:
            if e.reason == " Not authorized.":
                self.end()
                raise
            else:
                twitterLogger.exception('TweepError caught!')
                return self.next()

    #@twitterLogger.debug()
    def end(self):
        returnClient(self.client)