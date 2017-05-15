import re, requests
from sys import maxsize as MAX_INT
import time
from .globals import *
#import facebook
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS


class Client:

    name = "Unnamed Facebook Client"


    def __str__(self):
        return self.name


    def __init__(self, **kwargs):
        self.access_token = kwargs['access_token']
        if not self.access_token: raise NullAccessTokenException()
        if "name" in kwargs:
            self.name = kwargs['name']
        #self.graph = facebook.GraphAPI(access_token=self.access_token)
        if not FACEBOOK_APP_PARAMS['version']:
            raise Exception("Please set FACEBOOK_APP_PARAMS values in settings")
        self.baseURL = 'https://graph.facebook.com/%s/' % FACEBOOK_APP_PARAMS['version']

    def get(self, node, **kwargs):
        url = self.baseURL + node + '?access_token=' + self.access_token
        if 'fields' in kwargs:
            strFields = self.fieldify(kwargs['fields'])
            url += '&fields=' + strFields
            kwargs.pop('fields')
        for kwarg in kwargs.keys():
            if kwargs[kwarg]:
                url += '&%s=%s' % (kwarg, kwargs[kwarg])
        #log('calling: %s'%url)
        response = requests.get(url).json()
        #log('response:')
        #pretty(response)
        self.lastRequestAt = time.time()
        if 'error' in response.keys():
            raise Exception(response['error'])
        return response

    def fieldify(self, jfields):
        s = ''
        for item in jfields:
            if isinstance(item, dict):
                for key in item.keys():
                    s += key
                    if isinstance(item[key], list):
                        s += '{' + self.fieldify(item[key]) + '}'
            else:
                s += item
            s += ','
        return s[:-1]

    def getNext(self, response):
        nextResponse = None
        if 'paging' in response and 'next' in response['paging']:
            url = response['paging']['next']
            nextResponse = requests.get(url)
            nextResponse = nextResponse.json()
        return nextResponse



class ClientItterator:

    lastResponse = {}
    dataIndex = 0
    until = None
    pagingToken = None
    after = None

    def __init__(self, node, **kwargs):
        self.node = node
        self.kwargs = kwargs

    #@facebookLogger.debug(showArgs=True,showClass=True)
    def call(self):
        self.lastResponse = None
        self.dataIndex = 0
        client = getClient()
        try:
            response = client.get(self.node,
                                  until=self.until,
                                  __paging_token=self.pagingToken,
                                  after=self.after,
                                  **self.kwargs)
            self.setLastResponse(response)
            #log('lastResponse: %s'%self.lastResponse)
        except Exception as e:
            returnClient(client)
            raise e
        returnClient(client)


    def setLastResponse(self, jResponse):
        if "data" in jResponse:
            self.lastResponse = jResponse
        else:
            for key in jResponse.keys():
                if isinstance(jResponse[key], dict) and "data" in jResponse[key]:
                    self.lastResponse = jResponse[key]

    #@facebookLogger.debug(showArgs=True, showClass=True)
    def next(self):
        item = None
        if not self.lastResponse:
            self.call()
        if self.dataIndex < len(self.lastResponse['data']):
            item = self.lastResponse['data'][self.dataIndex]
            self.dataIndex += 1
            return item
        elif "paging" in self.lastResponse and "next" in self.lastResponse['paging']:
            self.until, self.pagingToken, self.after = self.getPagingToken()
            if not self.until and not self.after:
                return None
            self.call()
            return self.next()

    #@facebookLogger.debug(showArgs=True, showClass=True)
    def getPagingToken(self):
        if self.lastResponse and \
                        "paging" in self.lastResponse and \
                        "next" in self.lastResponse['paging']:
            #log(self.lastResponse['paging']['next'])
            until = pagingToken = after = None
            nextURL = self.lastResponse['paging']['next']

            match = re.match(r".+until=(?P<until>\w+).*", nextURL)
            if match: until = int(match.group('until'))-1

            match = re.match(r".+__paging_token=(?P<token>\w+).*", nextURL)
            if match: pagingToken = match.group('token')

            match = re.match(r".+after=(?P<after>\w+).*", nextURL)
            if match: after = match.group('after')

            return until, pagingToken, after


def getClient():
    client = None
    while not client:
        if not clientQueue.empty():
            client = clientQueue.get()
    return client


def returnClient(client):
    assert not clientQueue.full(), "Client Queue is already full. There is a Client that has been returned twice!"
    clientQueue.put(client)


def createClient(profile):
    try:
        client = Client(
            name = "%s's facebook App"%profile.user,
            access_token = profile.fbAccessToken._token
        )
        return client
    except NullAccessTokenException:
        profile.facebookApp_parameters_error = True
        profile.save()
        facebookLogger.exception('%s has got an invalid Facebook app'%profile.user)
        return None


class ExitFlagRaised(Exception):
    pass


class NullAccessTokenException(Exception):
    def __init__(self): super(NullAccessTokenException, self).__init__("Access token cannot be null")