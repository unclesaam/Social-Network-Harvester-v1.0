from .commonThread import *


class TwRetweeterHarvester(CommonThread):

    workQueueName = 'twRetweetUpdateQueue'
    batchSize = 1

    def method(self, tweets):
        tweet = tweets[0]
        client = getClient('retweets')
        try:
            response = client.call('retweets', id=tweet._ident)
        except tweepy.error.TweepError as e:
            log("TweepError retrieved: %s"%e.reason)
            if e.api_code == 200: # unauthorized
                tweet._error_on_retweet_harvest = True
            elif e.api_code == 34: # page doesn't exists
                tweet.deleted_at = today()
            tweet.save()
            returnClient(client)
            return
        returnClient(client)
        for retweet in response:
            jretweet = retweet._json
            retweet, new = Tweet.objects.get_or_create(_ident=jretweet['id'])
            if new:
                retweet.UpdateFromResponse(jretweet)
        tweet._last_retweeter_harvested = today()
        tweet.save()
