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
    }

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

    #@twitterLogger.debug()
    def call(self, callName, *args, **kwargs):
        if time.time() >= self.getResetTime(callName):
            self.refreshLimits()
        remainingCalls = self.getRemainingCalls(callName)
        if remainingCalls > 0:
            self.setRemainingCalls(callName, remainingCalls-1)
            return getattr(self.api, callName)(*args, **kwargs)
        else:
            raise Exception('No more calls of type %s'%self.callsMap[callName])

    @twitterLogger.debug()
    def refreshLimits(self):
        response = self.api.rate_limit_status()
        self.limits = response['resources']
        #self.updateRefreshTimer()

    #@twitterLogger.debug()
    def getRemainingCalls(self, callName):
        callIdentifier = self.callsMap[callName]
        if time.time() >= self.refreshTimer:
            self.refreshLimits()
        return self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['remaining']

    #@twitterLogger.debug()
    def setRemainingCalls(self, callName, value):
        callIdentifier = self.callsMap[callName]
        if time.time() >= self.refreshTimer:
            self.refreshLimits()
        self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['remaining'] = value

    #@twitterLogger.debug()
    def getResetTime(self, callName):
        callIdentifier = self.callsMap[callName]
        #log('item found: %s'%re.search(r'(?<=/)\w+(?=/)', callIdentifier))
        return self.limits[re.search(r'(?<=/)\w+(?=/)', callIdentifier).group(0)][callIdentifier]['reset']

    '''
    #@twitterLogger.debug()
    def updateRefreshTimer(self):
        self.refreshTimer = MAX_INT
        for callName in self.callsMap:
            #log('callIdentifier: %s'%callIdentifier)
            newTimer = self.getResetTime(callName)
            if newTimer < self.refreshTimer:
                self.refreshTimer = newTimer
    '''