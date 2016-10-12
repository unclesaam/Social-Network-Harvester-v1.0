from .commonThread import *

class TweetUpdater(CommonThread):

    batchSize = 100
    workQueueName = 'tweetUpdateQueue'


    def method(self, tweetList):
        client = getClient('statuses_lookup')
        responses = client.call('statuses_lookup', id_=[tweet._ident for tweet in tweetList], trim_user=True)
        returnClient(client)
        for response in responses:
            if threadsExitFlag[0]: return
            tweet = next((tweet for tweet in tweetList if tweet._ident == response._json['id']), None)
            if tweet:
                tweet.UpdateFromResponse(response._json)
                tweetList.remove(tweet)
        for tweet in tweetList:
            log('%s has been deleted'%tweet)
            tweet.deleted_at = today()
            tweet.save()
        #log("just updated %s tweets"%(self.lookupBatchSize-len(tweetList)))