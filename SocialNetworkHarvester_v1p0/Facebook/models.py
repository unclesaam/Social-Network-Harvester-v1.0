from django.db import models
from SocialNetworkHarvester_v1p0.settings import FACEBOOK_APP_PARAMS
import requests, time, re

from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG
log = lambda s: facebookLogger.log(s) if DEBUG else 0
pretty = lambda s: facebookLogger.pretty(s) if DEBUG else 0

class AccessToken(models.Model):

    class Meta:
        app_label = "Facebook"

    _token = models.CharField(max_length=255)
    expires = models.IntegerField(blank=True,null=True)
    # expires gives the "epoch date" of expiration of the token. Compare to time.time() to know if still valid.

    def is_expired(self):
        return time.time() >= self.expires

    def is_extended(self):
        return self.expires != None

def setFBToken(newToken):
    token = None
    if AccessToken.objects.count() > 1 :
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    if not token:
        token = AccessToken.objects.create()
    token._token = newToken
    token.expires = None
    token.save()
    extendFBToken(token)

def extendFBToken(token):
    if token.is_extended():
        raise Exception('The token is already extended, the extension process needs a short-lived token.')
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'%(FACEBOOK_APP_PARAMS['app_id'],FACEBOOK_APP_PARAMS['secret_key'],token._token)
    response = requests.get(url)
    text = response.text
    newToken, expires = text.split('&')
    token._token = re.sub('.*=', '', newToken)
    token.expires = int(time.time() + int(re.sub('.*=', '', expires)))
    token.save()

def getFBToken():
    token = None
    if AccessToken.objects.count() > 1:
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    return token
