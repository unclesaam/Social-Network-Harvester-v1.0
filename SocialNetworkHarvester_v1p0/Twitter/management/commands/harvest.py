
from AspiraUser.models import UserProfile
from django.contrib.auth.models import User
from django.utils.timezone import utc
from datetime import datetime
import tweepy
from Twitter.models import TWUser, friend

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
            usersToHarvest = profile.twitterUsersToHarvest.filter(_error_on_update=False)
            updater = twUserListUpdater(client, usersToHarvest)
            log('launching update for %s'%profile)
            updater.launchUpdate()
            for twUser in usersToHarvest.all():
                friendsUpdater = twFriendshipUpdater(client, twUser)
                log('launching friends update for %s'%twUser)
                friendsUpdater.launchUpdate()
        except:
            twitterLogger.exception("An error occured while updating TWUsers on %s"%profile)
            if DEBUG: raise
        finally:
            profile._last_tw_update = datetime.utcnow().replace(tzinfo=utc)
            profile.save()


########## Common ##########

def today():
    return datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

@twitterLogger.debug()
def createUpdateList(queryset):
    ordered_elements = queryset.filter(_last_updated__isnull=True) | \
                       queryset.filter(_last_updated__lt=today()).order_by('_last_updated')
    #log('ordered_elements: %s'%ordered_elements)
    return ordered_elements

@twitterLogger.debug()
def createTwClient(profile):
    ck = profile.twitterApp_consumerKey
    cs = profile.twitterApp_consumer_secret
    atk = profile.twitterApp_access_token_key
    ats = profile.twitterApp_access_token_secret
    auth = tweepy.OAuthHandler(ck, cs)
    auth.set_access_token(atk, ats)
    return tweepy.API(auth)

@twitterLogger.debug()
def clearUpdatedTime():
    for profile in UserProfile.objects.filter(_last_tw_update__isnull=False):
        profile._last_tw_update = None
        profile.save()
    for twUser in TWUser.objects.filter(_last_updated__isnull=False):
        twUser._last_updated = None
        twUser.save()


class commonTwClass:

    remainingCalls = 0
    callsResetTime = 0

    def __init__(self, client):
        self.client = client

    @twitterLogger.debug()
    def needToWait(self):
        raise Exception('No more calls available.')

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



######### Classes #########

class twUserListUpdater(commonTwClass):

    userLookupBatchSize = 200

    def __init__(self, client, twUserList):
        self.twUserList = twUserList
        super().__init__(client)

    @twitterLogger.debug()
    def launchUpdate(self):
        all_users = createUpdateList(self.twUserList)
        lists = [all_users[i:i+self.userLookupBatchSize] for i in range(0, len(all_users), self.userLookupBatchSize)]
        self.updateAppCallStatus()
        for list in lists:
            if self.remainingCalls > 0:
                log('remaining /users/lookup calls = %s'%self.remainingCalls)
                self.updateTWuserList(list)
                self.remainingCalls -= 1
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

    @twitterLogger.debug()
    def updateAppCallStatus(self):
        response = self.client.rate_limit_status()
        self.remainingCalls = response['resources']['users']['/users/lookup']['remaining']
        self.callsResetTime = response['resources']['users']['/users/lookup']['reset']


class twFriendshipUpdater(commonTwClass):

    userLookupBatchSize = 200

    def __init__(self, client, twUser):
        self.twUser = twUser
        super().__init__(client)

    @twitterLogger.debug()
    def launchUpdate(self):
        newTwUsers = []
        allFriendsIds = []
        log('twUser: %s'%self.twUser)
        cursor = tweepy.Cursor(self.client.friends_ids, screen_name=self.twUser.screen_name).items()
        twid = True
        while twid:
            twid = self.getNextFromCursor(cursor)
            allFriendsIds.append(twid)
            twFriend, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
                newTwUsers.append(twFriend)
            if not self.twUser.friends.filter(value=twFriend, ended__isnull=True).exists():
                friendship = friend.objects.create(value=twFriend, twuser=self.twUser)
                self.twUser.friends.add(friendship)
                self.twUser.save()
            page = self.getNextFromCursor(cursor)

        self.endOldFriendships(allFriendsIds)

        twUserUpdater = twUserListUpdater(client, newTwUsers)
        twUserUpdater.launchUpdate()

    @twitterLogger.debug()
    def endOldFriendships(self, allFriendsIds):
        for friendship in self.twUser.friends.filter(ended__isnull=True):
            if friendship.value._ident not in allFriendsIds:
                friendship.ended = today()
                friendship.save()

    @twitterLogger.debug()
    def updateAppCallStatus(self):
        response = self.client.rate_limit_status()
        self.remainingCalls = response['resources']['friends']['/friends/ids']['remaining']
        self.callsResetTime = response['resources']['friends']['/friends/ids']['reset']



class twFriendOflistUpdater(commonTwClass):
    pass

class twFollowerlistUpdater(commonTwClass):
    pass

class twFollowedlistUpdater(commonTwClass):
    pass

class twFavoriteTweetUpdater(commonTwClass):
    pass



class twUserHarvester(commonTwClass):
    pass

class twHashtagHarvester(commonTwClass):
    pass