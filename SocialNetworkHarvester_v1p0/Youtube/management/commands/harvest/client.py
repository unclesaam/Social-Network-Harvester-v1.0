
from .globals import *
from apiclient.discovery import build
from apiclient.errors import HttpError

class Client():

    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.api = build("youtube", "v3", developerKey=apiKey)
        self.reset()
        self.testApi()

    def __str__(self):
        return 'Youtube API client (%s)'%(self.apiKey)

    def testApi(self):
        self.api.i18nLanguages().list(part='snippet').execute()

    def reset(self):
        self.call = None
        self.req = None
        self.response = None

    def list(self, callName, *args, **kwargs):
        self.reset()
        assert hasattr(self.api, callName), 'YT API has no %s method'%callName
        call = getattr(self.api, callName)
        assert callable(call), '%s is not a callable method'%callName
        self.call = call
        self.req = call().list(*args, **kwargs)
        self.response = self.req.execute()
        return self.response

    def next(self):
        assert self.call, 'Must first call "first()" method'
        self.req = self.call().list_next(self.req, self.response)
        self.response = self.req.execute()
        return self.response


def getClient():
    client = None
    while not client:
        if not clientQueue.empty():
            client = clientQueue.get()
    return client

def returnClient(client):
    assert not clientQueue.full(),"Client Queue is already full. There is a Client that has been returned twice!"
    clientQueue.put(client)
