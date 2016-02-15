from .client import *
from SocialNetworkHarvester_v1p0.settings import LOG_DIRECTORY
import os

class CommonThread(threading.Thread):

    #@twitterLogger.debug()
    def __init__(self, threadName, clientQueue):
        #threading.Thread.__init__(self)
        super().__init__()
        self.clientQueue = clientQueue
        self.name = threadName

    @twitterLogger.debug()
    def run(self):
        try:
            self.execute()
        except Exception as e:
            exceptionQueueLock.acquire()
            exceptionQueue.put(e)
            exceptionQueueLock.release()
        finally:
            log('%s has finished'%threading.current_thread().name)
            #self.join()

    @twitterLogger.debug()
    def needToWait(self, callName=None):
        raise Exception('No more calls available.')

    '''
    def getNextFromCursor(self, cursor):
        if self.remainingCalls > 0:
            try:
                page = cursor.next()
            except tweepy.error.RateLimitError:
                self.needToWait()
                return self.getNextFromCursor(cursor)
            return page
        else:
            self.needToWait()
            self.remainingCalls = 1
            return getNextFromCursor(cursor)
    '''
    @twitterLogger.debug()
    def getClient(self, callName):
        client = None
        clientQueueLock.acquire()
        if not self.clientQueue.empty():
            client = self.clientQueue.get()
        clientQueueLock.release()
        while not client or client.getRemainingCalls(callName) <= 0 :
            clientQueueLock.acquire()
            if not self.clientQueue.empty():
                self.clientQueue.put(client)
                client = self.clientQueue.get()
            clientQueueLock.release()
        return client

    @twitterLogger.debug()
    def returnClient(self, client):
        clientQueueLock.acquire()
        self.clientQueue.put(client)
        clientQueueLock.release()