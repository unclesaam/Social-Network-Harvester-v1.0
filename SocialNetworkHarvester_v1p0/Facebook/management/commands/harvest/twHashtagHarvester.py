from .commonThread import *
from urllib.parse import quote
import urllib.request as req
from bs4 import BeautifulSoup as bs
import socket
import random


class TwHashtagHarvester(CommonThread):

    workQueueName = 'hashtagHarvestQueue'
    batchSize = 1

    def method(self, hashtagHarvesters):
        hashtagHarvester = hashtagHarvesters[0]
        hashtag = hashtagHarvester.hashtag
        max_id = None
        harvestCount = 0
        if not hashtagHarvester._has_reached_begining and \
                hashtagHarvester.harvested_tweets.filter(created_at__isnull=False).count() > 0:
            max_id = hashtagHarvester.harvested_tweets.filter(created_at__isnull=False).order_by('created_at')[0]._ident - 1
        log("max_id: %s"%max_id)
        alreadyExists = 0
        while not threadsExitFlag[0]:
            twids = []
            twids = self.fetch_tweets_from_html(hashtag.term, hashtagHarvester._harvest_since,
                                                hashtagHarvester._harvest_until, max_id)
            time.sleep(0.2)
            if len(twids) == 0:
                hashtagHarvester._has_reached_begining = True
                break
            for twid in twids:
                if not max_id or twid < max_id:
                    max_id = twid - 1
                twObj, new = Tweet.objects.get_or_create(_ident=twid)
                twObj.harvested_by.add(hashtagHarvester)
                twObj.hashtags.add(hashtag)
                twObj.save()
                if new:
                    #log("new Tweet created from %s"%hashtag)
                    alreadyExists = 0
                    tweetUpdateQueue.put(twObj)
                elif twObj.created_at != None:
                    alreadyExists += 1
                    #log("alreadyExists: %s"% alreadyExists)
                    if alreadyExists >= 10: # if 10 consecutive tweets already exists, break the loop.
                        break
                harvestCount += 1
                if harvestCount >= 10000:
                    break
            #log('twids: %s' % twids)
        log("harvest finished for %s"% hashtagHarvester)
        hashtagHarvester._last_harvested = today()
        hashtagHarvester.save()

    #@twitterLogger.debug(showArgs=True)
    def fetch_tweets_from_html(self, query, since, until, max_id=None):
        params = '%s since:%s-%s-%s until:%s-%s-%s' % (query, since.year,
                                                since.month,since.day, until.year,
                                                until.month,until.day)
        if max_id: params += ' max_id:%s' % max_id
        strUrl = 'https://twitter.com/hashtag/' + quote(params)
        #log('strUrl: %s'%strUrl)
        url = req.Request(strUrl, headers={
            'User-Agent': random.choice(USER_AGENTS)})
        try:
            data = req.urlopen(url, timeout=5)
            page = bs(data, "html.parser")
        except socket.timeout:
            log("html loading failed, retrying in 1 sec")
            time.sleep(1)
            return self.fetch_tweets_from_html(query,since,until,max_id)
        tweets = page.find_all('li', {"data-item-type": "tweet"})
        tweet_list = [int(tweet['data-item-id']) for tweet in tweets if tweet.has_attr('data-item-id')]
        return tweet_list


USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.36 Safari/525.19',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.540.0 Safari/534.10',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.4 (KHTML, like Gecko) Chrome/6.0.481.0 Safari/534.4',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.86 Safari/533.4',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/4.0.223.3 Safari/532.2',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.201.1 Safari/532.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.27 Safari/532.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/2.0.173.1 Safari/530.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.558.0 Safari/534.10',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.600.0 Safari/534.14',
    'Mozilla/5.0 (X11; U; Windows NT 6; en-US) AppleWebKit/534.12 (KHTML, like Gecko) Chrome/9.0.587.0 Safari/534.12',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.0 Safari/534.13',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.11 Safari/534.16',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20',
    'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.792.0 Safari/535.1',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.872.0 Safari/535.2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
    'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.3',
]