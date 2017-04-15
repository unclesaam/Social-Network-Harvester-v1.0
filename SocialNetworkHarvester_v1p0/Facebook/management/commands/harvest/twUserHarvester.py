from .commonThread import *


class TwUserHarvester(CommonThread):

    workQueueName = 'userHarvestQueue'
    batchSize = 1

    def method(self, twUsers):
        twUser = twUsers[0]
        allTweetsIds = []
        harvestCount = 0
        cursor = CustomCursor('user_timeline', screen_name=twUser.screen_name, id=twUser._ident, count=200)
        if not twUser._has_reached_begining and twUser.tweets.count() > 0:
            cursor.pagination_item = twUser.tweets.order_by('created_at')[0]._ident - 1
        alreadyExists = 0
        while not threadsExitFlag[0]:
            tweet = None
            try:
                tweet = cursor.next()
                #log('tweet: %s'%tweet)
            except tweepy.error.TweepError as e:
                if e.reason == " Not authorized.":
                    log('%s %s call has returned "Not authorized"'%(twUser, 'user_timeline'))
                    twUser.protected = True
                    twUser.save()
                if e.api_code == 34:
                    log('%s has returned no result.'%twUser)
                    twUser._error_on_harvest = True
                    twUser.save()
                break
            if not tweet:
                twUser._has_reached_begining = True
                break
            jObject = tweet._json
            allTweetsIds.append(jObject['id'])
            #log('len(allTweetsIds): %s'%len(allTweetsIds))
            twObj, new = Tweet.objects.get_or_create(_ident=jObject['id'])
            if new:
                alreadyExists = 0
                twObj.UpdateFromResponse(jObject)
                twRetweetUpdateQueue.put(twObj)
            elif twObj.created_at != None:
                alreadyExists += 1
                if alreadyExists >= 10:
                    break
            harvestCount += 1
            if harvestCount >= 10000: break
        twUser._last_tweet_harvested = today()
        twUser.save()
