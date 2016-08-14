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
        'retweets': '/statuses/retweets/:id',
        'statuses_lookup': '/statuses/lookup',
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


    #@twitterLogger.debug()
    def call(self, callName, *args, **kwargs):
        if time.time() >= self.getResetTime(callName)+1:
            self.refreshLimits()
        remainingCalls = self.getRemainingCalls(callName)
        if remainingCalls > 0:
            self.setRemainingCalls(callName, remainingCalls-1)
            return getattr(self.api, callName)(*args, **kwargs)
            '''try:
                return getattr(self.api, callName)(*args, **kwargs)
            except requests.exceptions.RequestException:
                time.sleep(2)
                return call(callName, *args, **kwargs)'''
        else:
            raise Exception('No more calls of type "%s"'%self.callsMap[callName])

    #@twitterLogger.debug()
    def refreshLimits(self):
        response = self.api.rate_limit_status()
        self.limits = response['resources']
        self.prettyLimitStatus()

    #@twitterLogger.debug()
    def getRemainingCalls(self, callName):
        if time.time() >= self.getResetTime(callName)+1:
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


#@twitterLogger.debug()
def getClient(callName):
    client = None
    #log("%i clients available"%clientQueue.qsize())
    if not clientQueue.empty():
        client = clientQueue.get()
    while not client or client.getRemainingCalls(callName) <= 0 :
        if client:
            clientQueue.put(client)
            client = None
        if not clientQueue.empty():
            client = clientQueue.get()
    #log('valid client found: %s.'%client)
    return client

#@twitterLogger.debug(showArgs=True)
def returnClient(client):
    if clientQueue.full():
        #log("clients: %s"%[client for client in iter(clientQueue.get, None)])
        raise Exception("Client Queue is already full. There is a Client that is returned twice!")
    else:
        clientQueue.put(client)
        #log("returned client. %i clients available"%clientQueue.qsize())



class CustomCursor:

    results = []
    index = 0
    nbItems = 0

    def __init__(self, callName, **kwargs):
        self.callName = callName
        self.kwargs = kwargs
        self.initPagination()

    #@twitterLogger.debug()
    def initPagination(self):
        client = getClient(self.callName)
        method = getattr(client.api, self.callName)
        if not hasattr(method, 'pagination_mode'):
            raise Exception("The API method must support pagination to be used with a Cursor.")
        elif method.pagination_mode == 'cursor':
            #log('cursor-type pagination')
            self.pagination_type = 'cursor'
            self.pagination_item = -1
        elif method.pagination_mode == 'page':
            #log('page-type pagination')
            self.pagination_type = 'page'
            self.pagination_item = 0
        elif method.pagination_mode == 'id':
            #log('id-type pagination')
            self.pagination_type = 'max_id'
            self.pagination_item = None
        returnClient(client)

    #@twitterLogger.debug()
    def next(self):
        if self.index == -1: return None
        if self.index < self.nbItems:
            item = self.results[self.index]
            self.index += 1
            return item
        else:
            self._getNextSet()
            return self.next()

    #@twitterLogger.debug()
    def _getNextSet(self):
        self.results = []

        self.kwargs[self.pagination_type] = self.pagination_item
        client = getClient(self.callName)
        try:
            if self.pagination_type == 'cursor':
                self.results, cursors = client.call(self.callName,**self.kwargs)
                self.pagination_item = cursors[1]
            elif self.pagination_type == 'max_id':
                self.results = client.call(self.callName,**self.kwargs)
                self.pagination_item = self.results.max_id
            elif self.pagination_type == 'page':
                self.results = client.call(self.callName,**self.kwargs)
                self.pagination_item += 1
            #log('%s: %s'%(self.pagination_type,self.pagination_item))
        except:
            #twitterLogger.exception('an error occured in cursor')
            returnClient(client)
            raise
        returnClient(client)
        self.nbItems = len(self.results)
        if self.nbItems == 0:
            self.index = -1 #means the iteration has finished
        else:
            self.index = 0
