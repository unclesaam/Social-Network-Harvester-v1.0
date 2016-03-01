from .commonThread import *


class TwRetweeterHarvester(CommonThread):

    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            if twRetweetUpdateQueue.qsize()%100==0:
                log("tweets left to retweet-Harvest: %s"%twRetweetUpdateQueue.qsize())
            tweet = twRetweetUpdateQueue.get()
            try:
                self.harvestRetweets(tweet)
            except:
                tweet._error_on_retweet_harvest = True
                twUser.save()
                log("%s's retweets query has raised an unmanaged error"%tweet)
                raise

    #@twitterLogger.debug(showArgs=True)
    def harvestRetweets(self, tweet):
        client = getClient('retweets')
        try:
            response = client.call('retweets', id=tweet._ident)
        except tweepy.error.TweepError:
            twitterLogger.exception('TweepError caught with %s'%tweet)
            #tweet._error_on_retweet_harvest = True
            #tweet.save()
            returnClient(client)
            return None
        returnClient(client)
        for retweet in response:
            jretweet = retweet._json
            retweet, new = Tweet.objects.get_or_create(_ident=jretweet['id'])
            if new:
                retweet.UpdateFromResponse(jretweet)
        tweet._last_retweeter_harvested = today()
        tweet.save()
