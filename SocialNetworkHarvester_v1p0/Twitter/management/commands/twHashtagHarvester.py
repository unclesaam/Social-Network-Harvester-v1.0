from .commonThread import *
from urllib.parse import quote
import urllib.request as req
from bs4 import BeautifulSoup as bs

class TwHashtagHarvester(CommonThread):
    @twitterLogger.debug()
    def execute(self):

        while not threadsExitFlag[0]:
            log("hashtags left to harvest: %s" % hashtagHarvestQueue.qsize())
            hashtag = hashtagHarvestQueue.get()
            try:
                self.harvestTweets(hashtag)
            except:
                hashtag.save()
                log("%s's tweet-harvest routine has raised an unmanaged error" % hashtag)
                raise

    @twitterLogger.debug(showArgs=True)
    def harvestTweets(self, hashtag):
        max_id = None
        oldest_tweet = hashtag.harvested_tweets.order_by('created_at')
        if oldest_tweet.count() > 0 and oldest_tweet[0].created_at != hashtag._harvest_since:
            max_id = oldest_tweet[0]._ident - 1
        twids = self.fetch_tweets_from_html(hashtag.term, hashtag._harvest_since,
                                               hashtag._harvest_until, max_id)
        #log('twids: %s'%twids)
        alreadyExists = 0
        while not threadsExitFlag[0] and not twids == []:
            for twid in twids:
                if not max_id or twid < max_id:
                    max_id = twid - 1
                twObj, new = Tweet.objects.get_or_create(_ident=twid)
                twObj.harvested_by = hashtag
                twObj.save()
                twObj.hashtags.add(hashtag)
                if new:
                    alreadyExists = 0
                    tweetUpdateQueue.put(twObj)
                else:
                    alreadyExists += 1
                    if alreadyExists >= 5: #efficiency measure: if 5 consecutive tweets already exists, break the loop.
                        break
            twids = self.fetch_tweets_from_html(hashtag.term, hashtag._harvest_since,
                                                hashtag._harvest_until, max_id)
            #log('twids: %s' % twids)

        hashtag._last_harvested = today()
        hashtag.save()

    #@twitterLogger.debug(showArgs=True)
    def fetch_tweets_from_html(self, query, since, until, max_id=None):
        params = '%s since:%s-%s-%s until:%s-%s-%s' % (query, since.year,
                                                since.month,since.day, until.year,
                                                until.month,until.day)
        if max_id: params += ' max_id:%s' % max_id
        strUrl = 'https://twitter.com/hashtag/' + quote(params)
        #log('strUrl: %s'%strUrl)
        url = req.Request(strUrl, headers={'User-Agent': 'Mozilla/5.0'})
        data = req.urlopen(url, timeout=5)
        if not data:  # if twitter didn't respond in 5 seconds, retry.
            return self.fetch_tweets(query, since, until, max_id)
        page = bs(data, "html.parser")
        tweets = page.find_all('li', {"data-item-type": "tweet"})
        tweet_list = [int(tweet['data-item-id']) for tweet in tweets if tweet.has_attr('data-item-id')]
        return tweet_list