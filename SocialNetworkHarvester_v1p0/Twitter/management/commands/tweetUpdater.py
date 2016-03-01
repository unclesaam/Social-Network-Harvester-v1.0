from .commonThread import *

class TweetUpdater(CommonThread):

    lookupBatchSize = 100

    def execute(self):
        tweetList = []
        while not threadsExitFlag[0]:
            log("tweets left to update: %s"%tweetUpdateQueue.qsize())
            while len(tweetList) < self.lookupBatchSize:
                if threadsExitFlag[0]: return
                if not tweetUpdateQueue.empty():
                    tweet = tweetUpdateQueue.get()
                    tweetList.append(tweet)
            self.updateTweetList(tweetList)
            tweetList = []
        if threadsExitFlag[0]: return
        self.updateTweetList(tweetList)
        tweetList = []

    def updateTweetList(self, tweetList):
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
            log('%s has returned no result'%tweet)
            tweet._error_on_update = True
            tweet.save()