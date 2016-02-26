from django.db import models
import _mysql_exceptions
from SocialNetworkHarvester_v1p0.models import *
from django.utils.timezone import utc
import json
from datetime import datetime
from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
import re

log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0
today = lambda : datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)


############### PLACE ####################

class TWPlace(models.Model):
    #class Meta:
     #   app_label = "Twitter"
    _ident = models.BigIntegerField(unique=True)


############## HASHTAG ###################
class Hashtag(models.Model):
    class Meta:
        app_label = "Twitter"
    pass

############### TWUSER ###################
class TWUser(models.Model):
    screen_name = models.CharField(max_length=255, null=True, blank=True)
    _ident = models.BigIntegerField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(null=True)
    geo_enabled = models.BooleanField(default=False)
    has_extended_profile = models.BooleanField(default=False)
    is_translation_enabled = models.BooleanField(default=False)
    is_translator = models.BooleanField(default=False)
    lang = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=255)
    profile_background_color = models.CharField(max_length=50)
    profile_background_image_url = models.CharField(max_length=500, null=True)
    profile_image_url= models.CharField(max_length=255)
    protected = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    time_zone = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=500, null=True)
    statuses_count = models.IntegerField(null=True)
    favourites_count = models.IntegerField(null=True)
    followers_count = models.IntegerField(null=True)
    friends_count = models.IntegerField(null=True)
    listed_count = models.IntegerField(null=True)

    _date_time_fields = ['created_at']
    _time_labels = ['screen_name', 'name', 'time_zone', 'url', 'description',
                   'statuses_count','favourites_count','followers_count','friends_count','listed_count']

    _last_updated = models.DateTimeField(null=True)
    _last_tweet_harvested = models.DateTimeField(null=True)
    _last_friends_harvested = models.DateTimeField(null=True)
    _last_followers_harvested = models.DateTimeField(null=True)
    _last_fav_tweet_harvested = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _error_on_harvest = models.BooleanField(default=False)
    _error_on_network_harvest = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1) # 1 = every day, 2 = every 2 days, etc.
    _harvest_frequency = models.IntegerField(default=1)
    _network_harvest_frequency = models.IntegerField(default=1)

    class Meta:
        app_label = "Twitter"

    def __str__(self):
        if self.screen_name:
            return self.screen_name
        elif self._ident:
            return 'TWUser #%s'%self._ident
        else:
            return 'Unidentified TWUser'

    def __init__(self, *args, **kwargs):
        super(TWUser, self).__init__(*args, **kwargs)
        if 'jObject' in kwargs: self.UpdateFromResponse(kwargs['jObject'])


    #@twitterLogger.debug(showArgs=False)
    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        #log('len(location): %s'%len(jObject['location']))
        #log('location: %s'%jObject['location'])
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateTimeLabels(jObject)
        self._ident = jObject['id']
        self._last_updated = today()
        self.save()

    #@twitterLogger.debug()
    def getLast(self, related_name):
        queryset = getattr(self, related_name).order_by('-recorded_time')
        if queryset.count() == 0:
            return None
        return queryset[0]


    #@twitterLogger.debug()
    def copyBasicFields(self, jObject):
        for atr in [x.attname for x in self._meta.fields if x not in self._date_time_fields and x.attname[0]!= '_']:
            if atr in jObject and atr !='id':
                setattr(self, atr, jObject[atr])

    #@twitterLogger.debug()
    def copyDateTimeFields(self, jObject):
        for atr in self._date_time_fields:
            if atr in jObject:
                dt = datetime.strptime(jObject[atr], '%a %b %d %H:%M:%S %z %Y')
                setattr(self, atr, dt)

    #@twitterLogger.debug()
    def updateTimeLabels(self, jObject):
        for atr in self._time_labels:
            if atr in jObject and jObject[atr]:
                related_name = atr+'s'
                lastItem = self.getLast(related_name)
                if not lastItem:
                    className = globals()[atr]
                    newItem = className(twuser=self, value=jObject[atr])
                    newItem.save()
                elif lastItem.value != jObject[atr]:
                    if lastItem.recorded_time == today():
                        lastItem.value = jObject[atr]
                        lastItem.save()

class screen_name(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="screen_names")
class name(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="names")
class time_zone(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="time_zones")
class url(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="urls")
class description(Text_time_label):
    twuser = models.ForeignKey(TWUser, related_name="descriptions")

class statuses_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="statuses_counts")
class favourites_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="favourites_counts")
class followers_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="followers_counts")
class friends_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="friends_counts")
class listed_count(Integer_time_label):
    twuser = models.ForeignKey(TWUser, related_name="listed_counts")

class friend(time_label):
    twuser = models.ForeignKey(TWUser, related_name="friends")
    value = models.ForeignKey(TWUser, related_name='friend_of')
    ended = models.DateTimeField(null=True)

class follower(time_label):
    twuser = models.ForeignKey(TWUser, related_name="followers")
    value = models.ForeignKey(TWUser, related_name='follower_of')
    ended = models.DateTimeField(null=True)


############### TWEET ####################
class Tweet(models.Model):
    class Meta:
        app_label = "Twitter"

    _ident = models.BigIntegerField(unique=True)
    coordinates = models.CharField(max_length=255, null=True)
    contributors = models.ManyToManyField(TWUser, related_name="contributed_to")
    created_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    text = models.TextField(max_length=255, null=True)
    retweet_count = models.IntegerField(null=True)
    possibly_sensitive = models.BooleanField(default=False)
    place = models.ForeignKey(TWPlace, null=True)
    source = models.CharField(max_length=255, null=True)
    lang = models.CharField(max_length=128)
    withheld_copyright = models.BooleanField(default=False)
    withheld_in_countries = models.CharField(max_length=255)
    withheld_scope = models.CharField(max_length=32) #either “status” or “user”.
    in_reply_to_user = models.ForeignKey(TWUser, null=True, related_name="replied_by")
    in_reply_to_status = models.ForeignKey('self', null=True, related_name="replied_by")
    quoted_status = models.ForeignKey('self', null=True, related_name="quoted_by")
    retweet_of = models.ForeignKey('self', null=True, related_name="retweets")

    _last_updated = models.DateTimeField(null=True)
    _last_retweets_harvested = models.DateTimeField(null=True)
    _last_reply_harvested = models.DateTimeField(null=True)

    _date_time_fields = ['created_at']
    _time_labels = ['retweet_count']
    _relationals = ['place_id','in_reply_to_user_id','in_reply_to_status_id','quoted_status_id','retweet_of_id']

    #@twitterLogger.debug()
    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateTimeLabels(jObject)
        if "retweeted_status" in jObject:
            self.setRetweetOf(jObject['retweeted_status'])
        self._ident = jObject['id']
        try:
            self.save()
        except:
            text = self.text.encode('unicode-escape')
            #log('modified text: %s'%text)
            self.text = text
            self.save()


    @twitterLogger.debug(showArgs=True)
    def setRetweetOf(self, jObject):
        pass

    #@twitterLogger.debug()
    def copyBasicFields(self, jObject):
        atrs = [x.attname for x in self._meta.fields if
                (x not in self._date_time_fields and
                 x.attname[0]!= '_' and
                 x.attname not in self._relationals)]
        for atr in atrs:
            if atr in jObject and atr !='id':
                setattr(self, atr, jObject[atr])

    #@twitterLogger.debug()
    def copyDateTimeFields(self, jObject):
        for atr in self._date_time_fields:
            if atr in jObject:
                dt = datetime.strptime(jObject[atr], '%a %b %d %H:%M:%S %z %Y')
                setattr(self, atr, dt)

    #@twitterLogger.debug()
    def updateTimeLabels(self, jObject):
        for atr in self._time_labels:
            if atr in jObject and jObject[atr]:
                related_name = atr+'s'
                lastItem = self.getLast(related_name)
                if not lastItem:
                    className = globals()[atr]
                    newItem = className(tweet=self, value=jObject[atr])
                    newItem.save()
                elif lastItem.value != jObject[atr]:
                    if lastItem.recorded_time == today():
                        lastItem.value = jObject[atr]
                        lastItem.save()

    def getLast(self, related_name):
        queryset = getattr(self, related_name).order_by('-recorded_time')
        if queryset.count() == 0:
            return None
        return queryset[0]

class retweet_count(Integer_time_label):
    tweet = models.ForeignKey(Tweet, related_name="retweet_counts")

class favorite_tweet(time_label):
    twuser = models.ForeignKey(TWUser, related_name="favorite_tweets")
    value = models.ForeignKey(Tweet, related_name='favorite_of')
    ended = models.DateTimeField(null=True)



