
from AspiraUser.models import UserProfile
from django.contrib.auth.models import User
from django.utils.timezone import utc
from datetime import datetime
import tweepy
from Twitter.models import TWUser

from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0

@twitterLogger.debug()
def harvestTwitter():
    clearUpdatedTime()
    ordered_profiles = UserProfile.objects.filter(_last_tw_update__isnull=True) | \
                       UserProfile.objects.filter(_last_tw_update__lt=today()).order_by('_last_tw_update')
    log('ordered_profiles: %s'%ordered_profiles)
    for profile in ordered_profiles:
        client = createTwClient(profile)
        try:
            updater = twUserUpdater(profile, client)
            updater.launchUpdate()
        except:
            twitterLogger.exception("An error occured while updating TWUsers on %s"%profile)
            if DEBUG: raise
        finally:
            profile._last_tw_update = datetime.utcnow().replace(tzinfo=utc)
            profile.save()

########## Common ##########

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

#@twitterLogger.debug()
def createUpdateList(queryset):
    ordered_elements = queryset.filter(_last_updated__isnull=True) | \
                       queryset.filter(_last_updated__lt=today()).order_by('_last_updated')
    log('ordered_elements: %s'%ordered_elements)
    return ordered_elements

def createTwClient(profile):
    ck = profile.twitterApp_consumerKey
    cs = profile.twitterApp_consumer_secret
    atk = profile.twitterApp_access_token_key
    ats = profile.twitterApp_access_token_secret
    auth = tweepy.OAuthHandler(ck, cs)
    auth.set_access_token(atk, ats)
    return tweepy.API(auth)

def clearUpdatedTime():
    for profile in UserProfile.objects.all():
        profile._last_tw_update = None
        profile.save()
    for twUser in TWUser.objects.all():
        twUser._last_updated = None
        twUser.save()

class commonTwClass:

    remainingCalls = 0
    callsResetTime = 0

    def __init__(self, profile, client):
        self.profile = profile
        self.client = client



######### Classes #########

class twUserUpdater(commonTwClass):

    userLookupBatchSize = 200

    @twitterLogger.debug()
    def launchUpdate(self):
        all_users = createUpdateList(self.profile.twitterUsersToHarvest.filter(_error_on_update=False))
        lists = [all_users[i:i+self.userLookupBatchSize] for i in range(0, len(all_users), self.userLookupBatchSize)]
        self.updateAppCallStatus()
        for list in lists:
            if self.remainingCalls > 0:
                log('remainingCalls = %s'%self.remainingCalls)
                self.updateTWuserList(list)
            else:
                self.needToWait()

    @twitterLogger.debug()
    def updateTWuserList(self, TWUserList):
        responses = self.client.lookup_users(screen_names=[user.screen_name for user in TWUserList])
        for response in responses:
            user = next((user for user in TWUserList if user.screen_name == response._json['screen_name']), None)
            if user:
                user.UpdateFromResponse(response._json)
                TWUserList.remove(user)
        for user in TWUserList:
            log('%s has returned no result'%user)
            user._error_on_update = True
            user.save()

    def updateAppCallStatus(self):
        response = self.client.rate_limit_status()
        self.remainingCalls = response['resources']['users']['/users/lookup']['remaining']
        self.callsResetTime = response['resources']['users']['/users/lookup']['reset']

    def needToWait(self):
        pass


class twUserHarvester(commonTwClass):
    pass

class twHashtagHarvester(commonTwClass):
    pass