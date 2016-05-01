from .client import *
from SocialNetworkHarvester_v1p0.settings import LOG_DIRECTORY, DEBUG
import os

class CommonThread(threading.Thread):

    #@twitterLogger.debug()
    def __init__(self, threadName):
        super().__init__()
        self.name = threadName

    #@twitterLogger.debug()
    def run(self):
        try:
            self.execute()
            log('%s has finished gracefully'%self.name)
        except Exception as e:
            exceptionQueue.put((e, self.name))
            log('%s HAS ENCOUNTERED AN ERROR'%threading.current_thread().name.upper())
        finally:
            return 0
