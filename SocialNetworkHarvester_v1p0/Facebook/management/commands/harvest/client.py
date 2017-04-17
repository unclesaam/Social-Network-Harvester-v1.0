import re
from sys import maxsize as MAX_INT
import time
from .globals import *
import facebook


class Client:

    name = "Unnamed Facebook Client"

    def __str__(self):
        return self.name


    #@facebookLogger.debug()
    def __init__(self, **kwargs):
        self.access_token = kwargs['id']
        if not self.access_token: raise NullAccessTokenException()
        self.secret = kwargs['secret']
        if "name" in kwargs:
            self.name = kwargs['name']
        self.graph = facebook.GraphAPI(access_token=self.access_token)


    #@facebookLogger.debug()
    def call(self, callName, *args, **kwargs):
        if time.time() >= self.getResetTime(callName)+1:
            self.refreshLimits()
        remainingCalls = self.getRemainingCalls(callName)
        if remainingCalls > 0:
            self.setRemainingCalls(callName, remainingCalls-1)
            return getattr(self.api, callName)(*args, **kwargs)
        else:
            raise Exception('No more calls of type "%s"'%self.callsMap[callName])


class NullAccessTokenException(Exception):
    def __init__(self): super(NullAccessTokenException, self).__init__("Access token cannot be null")


#@facebookLogger.debug()
def getClient(callName):
    client = None
    #log("%i clients available"%clientQueue.qsize())
    if not clientQueue.empty():
        client = clientQueue.get()
    while not client or client.getRemainingCalls(callName) <= 0 :
        if threadsExitFlag[0]: raise ExitFlagRaised
        if client:
            clientQueue.put(client)
            client = None
        if not clientQueue.empty():
            client = clientQueue.get()
    #log('valid client found: %s.'%client)
    return client

#@facebookLogger.debug(showArgs=True)
def returnClient(client):
    if clientQueue.full():
        #log("clients: %s"%[client for client in iter(clientQueue.get, None)])
        raise Exception("Client Queue is already full. There is a Client that is returned twice!")
    else:
        clientQueue.put(client)
        #log("returned client. %i clients available"%clientQueue.qsize())


def createClient(profile):
    try:
        client = Client(
            name = "%s's facebook App"%profile.user,
            id = profile.facebookApp_id,
            secret = profile.facebookApp_secret,
        )
        return client
    except:
        profile.facebookApp_parameters_error = True
        profile.save()
        facebookLogger.exception('%s has got an invalid Facebook app'%profile.user)
        return None


class ExitFlagRaised(Exception):
    pass


class CustomCursor:

    results = []
    index = 0
    nbItems = 0

    def __init__(self, callName, **kwargs):
        self.callName = callName
        self.kwargs = kwargs
        self.initPagination()

    #@facebookLogger.debug()
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

    #@facebookLogger.debug()
    def next(self):
        if self.index == -1: return None
        if self.index < self.nbItems:
            item = self.results[self.index]
            self.index += 1
            return item
        else:
            self._getNextSet()
            return self.next()

    #@facebookLogger.debug()
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
            #facebookLogger.exception('an error occured in cursor')
            returnClient(client)
            raise
        returnClient(client)
        self.nbItems = len(self.results)
        if self.nbItems == 0:
            self.index = -1 #means the iteration has finished
        else:
            self.index = 0
