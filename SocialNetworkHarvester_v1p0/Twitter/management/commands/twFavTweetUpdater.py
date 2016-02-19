from .commonThread import *



class TwFavTweetUpdater(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("twUsers left to fav-tweet-Harvest: %s"%favoriteTweetUpdateQueue.qsize())
            favoriteTweetUpdateQueueLock.acquire()
            twUser = favoriteTweetUpdateQueue.get()
            favoriteTweetUpdateQueueLock.release()
            try:
                self.harvestFavTweets(twUser)
            except:
                twUser._error_on_network_harvest = True
                twUser.save()
                twitterLogger.exception("%s's favorites query has raised an unmanaged error"%twUser)
                raise

    @twitterLogger.debug(showArgs=True)
    def harvestFavTweets(self, twUser):
        allFavTweetsIds = []

        cursor = CursorWrapper('favorites', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            twid = None
            try:
                twid = cursor.next()
            except tweepy.error.TweepError:
                log("TWUser %s is protected!")
                twUser.protected = True
                twUser.save()
            if not twid: break
            allFavTweetsIds.append(twid)
            tweet, new = Tweet.objects.get_or_create(_ident=twid)
            if new:
                tweetUpdateQueueLock.acquire()
                tweetUpdateQueue.put(twFriend)
                tweetUpdateQueueLock.release()
            if not twUser.favorite_tweets.filter(value=tweet, ended__isnull=True).exists():
                favorite = favorite_tweet.objects.create(value=tweet, twuser=twUser)

        if threadsExitFlag[0]: cursor.end() # returns the client, in case other threads are waiting for it.
        self.endOldFavorites(twUser, allFavTweetsIds)
        twUser._last_friends_harvested = today()
        twUser.save()


    @twitterLogger.debug()
    def endOldFavorites(self, twUser, allFavTweetsIds):
        log('%s has currently got %s favorite tweets'%(twUser, len(allFavTweetsIds)))
        for favorite in twUser.favorite_tweets.filter(ended__isnull=True):
            if threadsExitFlag[0]: return
            if favorite.value._ident not in allFavTweetsIds:
                favorite.ended = today()
                favorite.save()