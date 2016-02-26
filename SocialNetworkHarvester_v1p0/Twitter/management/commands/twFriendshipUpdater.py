from .commonThread import *

class TwFriendshipUpdater(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("twUsers left to friend-Harvest: %s"%friendsUpdateQueue.qsize())
#            friendsUpdateQueueLock.acquire()
            twUser = friendsUpdateQueue.get()
#            friendsUpdateQueueLock.release()
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

        cursor = CursorWrapper('friends_ids', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            twid = None
            try:
                twid = cursor.next()
            except tweepy.error.TweepError as e:
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
            #log('twid: %i'%twid)
            allFriendsIds.append(twid)
            twFriend, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
#                updateQueueLock.acquire()
                updateQueue.put(twFriend)
#                updateQueueLock.release()
            if not twUser.friends.filter(value=twFriend, ended__isnull=True).exists():
                friendship = friend.objects.create(value=twFriend, twuser=twUser)

        if threadsExitFlag[0]: cursor.end() # returns the client, in case other threads are waiting for it.
        self.endOldFriendships(twUser, allFriendsIds)
        twUser._last_friends_harvested = today()
        twUser.save()


    @twitterLogger.debug()
    def endOldFriendships(self, twUser, allFriendsIds):
        log('%s has currently got %s friends'%(twUser, len(allFriendsIds)))
        for friendship in twUser.friends.filter(ended__isnull=True):
            if threadsExitFlag[0]: return
            if friendship.value._ident not in allFriendsIds:
                friendship.ended = today()
                friendship.save()
