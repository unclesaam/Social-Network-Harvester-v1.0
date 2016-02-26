from .commonThread import *

class TwFollowersUpdater(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("twUsers left to follower-Harvest: %s"%followersUpdateQueue.qsize())
#            followersUpdateQueueLock.acquire()
            twUser = followersUpdateQueue.get()
#            followersUpdateQueueLock.release()
            try:
                self.harvestFollowers(twUser)
            except:
                twUser._error_on_network_harvest = True
                twUser.save()
                log("%s's followers_ids query has raised an unmanaged error"%twUser)
                raise

    @twitterLogger.debug(showArgs=True)
    def harvestFollowers(self, twUser):
        allFollowersIds = []

        cursor = CursorWrapper('followers_ids', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            twid = None
            try:
                twid = cursor.next()
            except tweepy.error.TweepError as e:
                if e.reason == " Not authorized.":
                    log('%s %s call has returned "Not authorized"'%(twUser, 'favorites'))
                    twUser.protected = True
                    twUser.save()
                if e.api_code == 34:
                    log('%s has returned no result.'%twUser)
                    twUser._error_on_network_harvest = True
                    twUser.save()
            if not twid: break
            #log('twid: %i'%twid)
            allFollowersIds.append(twid)
            twFollower, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
#                updateQueueLock.acquire()
                updateQueue.put(twFollower)
#                updateQueueLock.release()
            if not twUser.followers.filter(value=twFollower, ended__isnull=True).exists():
                followership = follower.objects.create(value=twFollower, twuser=twUser)

        if threadsExitFlag[0]: cursor.end() # returns the client, in case other threads are waiting for it.
        self.endOldfollowership(twUser, allFollowersIds)
        twUser._last_followers_harvested = today()
        twUser.save()


    @twitterLogger.debug()
    def endOldfollowership(self, twUser, allFollowersIds):
        log('%s has currently got %s followers'%(twUser, len(allFollowersIds)))
        for followership in twUser.followers.filter(ended__isnull=True):
            if threadsExitFlag[0]: return
            if followership.value._ident not in allFollowersIds:
                followership.ended = today()
                followership.save()
