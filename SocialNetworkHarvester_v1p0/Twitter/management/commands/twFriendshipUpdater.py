from .commonThread import *

class TwFriendshipUpdater(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("twUsers left to friend-Harvest: %s"%friendsUpdateQueue.qsize())
            twUser = friendsUpdateQueue.get()
            try:
                self.harvestFriends(twUser)
            except:
                twUser._error_on_network_harvest = True
                twUser.save()
                log("%s's friends_ids query has raised an unmanaged error"%twUser)
                raise

    @twitterLogger.debug(showArgs=True)
    def harvestFriends(self, twUser):
        allFriendsIds = []

        cursor = CustomCursor('friends_ids', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            twid = None
            try:
                twid = cursor.next()
            except tweepy.error.TweepError as e:
                log("An error occured: %s"%e.reason)
                if e.reason == " Not authorized.":
                    log('%s %s call has returned "Not authorized"'%(twUser, 'favorites'))
                    twUser.protected = True
                    twUser.save()
                    return None
                if e.api_code == 34:
                    log('%s has returned no result.'%twUser)
                    twUser._error_on_network_harvest = True
                    twUser.save()
                    return None
            if not twid: break
            allFriendsIds.append(twid)
            #log('len(allFriendsIds): %s'%len(allFriendsIds))
            twFriend, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
                updateQueue.put(twFriend)
            if not twUser.friends.filter(twuser=twFriend, ended__isnull=True).exists():
                friendship = follower.objects.create(twuser=twFriend, value=twUser)

        self.endOldFriendships(twUser, allFriendsIds)
        twUser._last_friends_harvested = today()
        twUser.save()


    #@twitterLogger.debug()
    def endOldFriendships(self, twUser, allFriendsIds):
        log('%s has currently got %s friends'%(twUser, len(allFriendsIds)))
        for friendship in twUser.friends.filter(ended__isnull=True):
            if threadsExitFlag[0]: return
            if friendship.twuser._ident not in allFriendsIds:
                friendship.ended = today()
                friendship.save()
