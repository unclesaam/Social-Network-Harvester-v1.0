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

