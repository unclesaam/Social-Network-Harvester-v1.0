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
    name = "Unnamed client"

    def __str__(self):
        return self.name

    #@twitterLogger.debug()
    def __init__(self, **kwargs):
        ck = kwargs['ck']
        cs = kwargs['cs']
        atk = kwargs['atk']
        ats = kwargs['ats']
        if "name" in kwargs:
            self.name = kwargs['name']
        auth = tweepy.OAuthHandler(ck, cs)
        auth.set_access_token(atk, ats)
        self.api = tweepy.API(auth)
        self.refreshLimits()


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

    #@twitterLogger.debug()
    def refreshLimits(self):
        response = self.api.rate_limit_status()
        self.limits = response['resources']
        self.prettyLimitStatus()

    #@twitterLogger.debug()
    def getRemainingCalls(self, callName):
        if time.time() >= self.getResetTime(callName):
            self.refreshLimits()
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

    def prettyLimitStatus(self):
        d = {'client':str(self)}
        for callName in self.callsMap:
            callIdentifier = self.callsMap[callName]
            d["{:<20}".format(callName)] = "{}/{} (resets in {:0.0f} seconds)".format(
                    self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['remaining'],
                    self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['limit'],
                    self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['reset'] - time.time())
        pretty(d)


@twitterLogger.debug()
def getClient(callName):
    client = None
    log("%i clients available"%clientQueue.qsize())
    if not clientQueue.empty():
        client = clientQueue.get()
    while not client or client.getRemainingCalls(callName) <= 0 :
        if client:
            clientQueue.put(client)
            client = None
        if not clientQueue.empty():
            client = clientQueue.get()
            #log('got %s. Remaining "%s" calls: %i. Reset in %s seconds'%(client, callName, client.getRemainingCalls(callName),
            #                                                             int(client.getResetTime(callName)-time.time())))
    log('valid client found: %s.'%client)
    return client

@twitterLogger.debug(showArgs=True)
def returnClient(client):
    if clientQueue.full():
        log("clients: %s"%[client for client in iter(clientQueue.get, None)])
        raise Exception("Client Queue is already full. There is a Client that is returned twice!")
    else:
        clientQueue.put(client)
        log("returned client. %i clients available"%clientQueue.qsize())


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
            self.rotateClient()
            return self.next()

        except StopIteration:
            log("StopIteration caught!")
            self.end()
            return None

        except tweepy.error.TweepError as e:
            if e.response.status_code == 429:
                log('Limits reached, rotating cursor''s client')
                self.rotateClient()
                return self.next()
            else:
                twitterLogger.exception('TweepError caught!')
                self.end()
                raise

    @twitterLogger.debug()
    def rotateClient(self):
        #self.client.refreshLimits()
        nextCursor = None
        max_id = None
        if hasattr(self.cursor.page_iterator, 'next_cursor'):
            nextCursor = self.cursor.page_iterator.next_cursor
        if hasattr(self.cursor.page_iterator, 'max_id'):
            max_id = self.cursor.page_iterator.max_id
        self.client.setRemainingCalls(self.callName, 0)
        returnClient(self.client)
        self.client = getClient(self.callName)
        #self.client.refreshLimits()
        self.cursor = tweepy.Cursor(getattr(self.client.api, self.callName), max_id=max_id,cursor=nextCursor, **self.kwargs).items()
        #log("cursor: %s"%self.cursor)

    @twitterLogger.debug()
    def end(self):
        returnClient(self.client)