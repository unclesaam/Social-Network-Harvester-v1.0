from .commonThread import *



class TwFavTweetUpdater(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("twUsers left to fav-tweet-Harvest: %s"%favoriteTweetUpdateQueue.qsize())
#            favoriteTweetUpdateQueueLock.acquire()
            twUser = favoriteTweetUpdateQueue.get()
#            favoriteTweetUpdateQueueLock.release()
            try:
                self.harvestFavTweets(twUser)
            except:
                twUser._error_on_network_harvest = True
                twUser.save()
                log("%s's favorites tweets query has raised an unmanaged error"%twUser)
                raise

    @twitterLogger.debug(showArgs=True)
    def harvestFavTweets(self, twUser):
        allFavTweetsIds = []

        cursor = CursorWrapper('favorites', screen_name=twUser.screen_name, id=twUser._ident)
        while not threadsExitFlag[0]:
            status = None
            try:
                status = cursor.next()
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
            if not status: break
            jResponse = status._json
            #pretty(jResponse)
            twid = jResponse['id']
            allFavTweetsIds.append(twid)
            tweet, new = Tweet.objects.get_or_create(_ident=twid)
            if new:
                tweet.UpdateFromResponse(jResponse)
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