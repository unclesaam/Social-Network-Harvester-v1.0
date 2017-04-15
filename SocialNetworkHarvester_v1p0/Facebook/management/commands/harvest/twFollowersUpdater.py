from .commonThread import *


class TwFollowersUpdater(CommonThread):

    workQueueName = 'followersUpdateQueue'
    batchSize = 1

    def method(self, twUsers):
        twUser = twUsers[0]
        allFollowersIds = []

        cursor = CustomCursor('followers_ids', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            twid = None
            try:
                twid = cursor.next()
                #log('twid: %s'%twid)
            except tweepy.error.TweepError as e:
                log("An error occured: %s"%e.reason)
                if e.reason == " Not authorized.":
                    log('%s %s call has returned "Not authorized"'%(twUser, 'favorites'))
                    twUser.protected = True
                    twUser.save()
                if e.api_code == 34:
                    log('%s has returned no result.'%twUser)
                    twUser._error_on_network_harvest = True
                    twUser.save()
            if not twid: break
            allFollowersIds.append(twid)
            #log('len(allFollowersIds): %s'%len(allFollowersIds))
            twFollower, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
                updateQueue.put(twFollower)
            if not twUser.followers.filter(value=twFollower, ended__isnull=True).exists():
                followership = follower.objects.create(value=twFollower, twuser=twUser)

        self.endOldfollowership(twUser, allFollowersIds)
        twUser._last_followers_harvested = today()
        twUser.save()


    #@twitterLogger.debug()
    def endOldfollowership(self, twUser, allFollowersIds):
        log('%s has currently got %s followers'%(twUser, len(allFollowersIds)))
        for followership in twUser.followers.filter(ended__isnull=True):
            if threadsExitFlag[0]: return
            if followership.value._ident not in allFollowersIds:
                followership.ended = today()
                followership.save()
