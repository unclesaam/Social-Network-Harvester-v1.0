from django.db import models
from django.db.utils import IntegrityError
import _mysql_exceptions
from SocialNetworkHarvester_v1p0.models import *
from django.utils.timezone import utc
import json
from datetime import datetime
import re

from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
log = lambda s : twitterLogger.log(s) if DEBUG else 0
pretty = lambda s : twitterLogger.pretty(s) if DEBUG else 0
today = lambda : datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)


############### PLACE ####################

class TWPlace(models.Model):
    _ident = models.CharField(unique=True, max_length=255)
    attributes = models.CharField(max_length=500, null=True)
    bounding_box = models.CharField(max_length=500, null=True)
    country = models.CharField(max_length=128, null=True)
    full_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=128, null=True)
    place_type = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=255, null=True)

    class Meta:
        app_label = "Twitter"

    def __str__(self):
        if self.name:
            return self.name
        elif self.place_type and self._ident:
            return "%s #%s"%(self.place_type, self._ident)

    #@twitterLogger.debug(showArgs=True)
    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        self.copyBasicFields(jObject)
        self._ident = jObject['id']
        self.save()

    def copyBasicFields(self, jObject):
        for atr in [x.attname for x in self._meta.fields if  x.attname[0]!= '_']:
            if atr in jObject and atr !='id':
                setattr(self, atr, jObject[atr])

    def get_obj_ident(self):
        return "TWPlace__%s" % self.pk


################### HASHTAG ###################

class Hashtag(models.Model):
    # TODO: be able to order hashtags by hit_count in an SQL query
    class Meta:
        app_label = "Twitter"

    term = models.CharField(max_length=128, null=True)

    def __str__(self):
        return "#"+self.term

    def hit_count(self):
        return self.tweets.count()

    def get_obj_ident(self):
        return "Hashtag__%s"%self.pk

class HashtagHarvester(models.Model):
    class Meta:
        app_label = "Twitter"

    hashtag = models.ForeignKey(Hashtag, related_name="harvesters")
    _harvest_since = models.DateTimeField(null=True, blank=True)
    _harvest_until = models.DateTimeField(null=True, blank=True)
    _has_reached_begining = models.BooleanField(default=False)
    _last_harvested = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        since = "undefined"
        until = "undefined"
        if self._harvest_since :
            since = "%s-%s-%s"%(self._harvest_since.year, self._harvest_since.month, self._harvest_since.day)
        if self._harvest_until :
            until = "%s-%s-%s" % (self._harvest_until.year, self._harvest_until.month, self._harvest_until.day)
        return "#%s's harvester (%s - %s)" %(self.hashtag.term, since, until)

    def harvest_count(self):
        return self.harvested_tweets.count()

    def get_obj_ident(self):
        return "HashtagHarvester__%s" % self.pk



################### TWUSER ####################

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
    _has_reached_begining = models.BooleanField(default=False)

    class Meta:
        app_label = "Twitter"

    def get_obj_ident(self):
        return "TWUser__%s" % self.pk

    def __str__(self):
        if self.screen_name:
            return self.screen_name
        elif self._ident:
            return 'TWUser %s'%self._ident
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
                    if atr == 'url':
                        # having a class named "url" breaks the Django import system.
                        className = TWUrl
                    else:
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
class TWUrl(Text_time_label):
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
class follower(time_label):
    twuser = models.ForeignKey(TWUser, related_name="followers")
    value = models.ForeignKey(TWUser, related_name='friends') # "value" user is following "twuser", calls it it's friend
    ended = models.DateTimeField(null=True)


############### TWEET ####################

class Tweet(models.Model):
    class Meta:
        app_label = "Twitter"

    def __str__(self):
        return "%s tweet #%s"%(self.user, self._ident)

    def get_obj_ident(self):
        return "Tweet__%s" % self.pk

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
    user = models.ForeignKey(TWUser, related_name="tweets", null=True)
    in_reply_to_user = models.ForeignKey(TWUser, null=True, related_name="replied_by")
    in_reply_to_status = models.ForeignKey('self', null=True, related_name="replied_by")
    quoted_status = models.ForeignKey('self', null=True, related_name="quoted_by")
    retweet_of = models.ForeignKey('self', null=True, related_name="retweets")
    user_mentions = models.ManyToManyField(TWUser, related_name="mentions")

    hashtags = models.ManyToManyField(Hashtag, related_name='tweets')
    harvested_by = models.ManyToManyField(HashtagHarvester, related_name='harvested_tweets')

    _last_updated = models.DateTimeField(null=True)
    _last_retweeter_harvested = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _error_on_retweet_harvest = models.BooleanField(default=False)

    _date_time_fields = ['created_at']
    _time_labels = ['retweet_count']
    _relationals = ['place_id','in_reply_to_user_id','in_reply_to_status_id','quoted_status_id','retweet_of_id',
                    'user_id', 'hashtags_id']

    #@twitterLogger.debug(showArgs=True)
    def UpdateFromResponse(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Twitter must be passed as argument.')
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateTimeLabels(jObject)
        if "entities" in jObject:
            self.setUserMentions(jObject['entities'])
            self.setHashtags(jObject['entities'])
        if "retweeted_status" in jObject:
            self.setRetweetOf(jObject['retweeted_status'])
        if 'user' in jObject and not self.user:
            self.setUser(jObject['user'])
        if jObject['in_reply_to_user_id']:
            self.setInReplyToUser(screen_name=jObject['in_reply_to_screen_name'],_ident=jObject['in_reply_to_user_id'])
            #self.setInReplyToUser(screen_name=jObject['in_reply_to_screen_name'], _ident=jObject['in_reply_to_user_id'])
        if jObject['in_reply_to_status_id']:
            self.setInReplyToStatus(jObject['in_reply_to_status_id'])
        if 'quoted_status_id' in jObject:
            self.setQuotedStatus(jObject['quoted_status_id'])
        if jObject['place']:
            self.setPlace(jObject['place'])

        self._ident = jObject['id']
        try:
            self.save()
        except:
            text = self.text.encode('unicode-escape')
            #log('modified text: %s'%text)
            self.text = text
            self.save()

    def setUser(self, jObject):
        ident = jObject['id']
        screen_name = None
        if "screen_name" in jObject:
            screen_name = jObject['screen_name']
        twuser, new = get_from_any_or_create(TWUser, _ident=ident, screen_name=screen_name)
        self.user = twuser

    def setInReplyToStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.in_reply_to_status = tweet

    def setInReplyToUser(self, **kwargs):
        twuser, new = get_from_any_or_create(TWUser, **kwargs)
        self.in_reply_to_user = twuser

    def setQuotedStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.quoted_status = tweet

    def setRetweetOf(self, jObject):
        tweet, new = Tweet.objects.get_or_create(_ident=jObject['id'])
        if new:
            tweet.UpdateFromResponse(jObject)
        self.retweet_of = tweet

    def setPlace(self, jObject):
        ident = jObject['id']
        place, new = TWPlace.objects.get_or_create(_ident=ident)
        if new:
            place.UpdateFromResponse(jObject)
        self.place = place

    def copyBasicFields(self, jObject):
        atrs = [x.attname for x in self._meta.fields if
                (x not in self._date_time_fields and
                 x.attname[0]!= '_' and
                 x.attname not in self._relationals)]
        for atr in atrs:
            if atr in jObject and atr !='id':
                setattr(self, atr, jObject[atr])

    def copyDateTimeFields(self, jObject):
        for atr in self._date_time_fields:
            if atr in jObject:
                dt = datetime.strptime(jObject[atr], '%a %b %d %H:%M:%S %z %Y')
                setattr(self, atr, dt)

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

    #@twitterLogger.debug(showArgs=True)
    def setUserMentions(self, jObject):
        if "user_mentions" in jObject:
            for user_mention in jObject["user_mentions"]:
                #log("user_mention: %s"% user_mention)
                id = user_mention['id']
                screen_name = None
                if 'screen_name' in user_mention:
                    screen_name = user_mention['screen_name']
                twUser, new = get_from_any_or_create(TWUser, _ident=id, screen_name=screen_name)
                #log("twUser: %s"%twUser)
                self.user_mentions.add(twUser)

    def setHashtags(self, jObject):
        if "hashtags" in jObject:
            for hashtag in jObject['hashtags']:
                hashtagObj, new = get_from_any_or_create(Hashtag, term=hashtag['text'])
                self.hashtags.add(hashtagObj)

class retweet_count(Integer_time_label):
    tweet = models.ForeignKey(Tweet, related_name="retweet_counts")

class favorite_tweet(time_label):
    twuser = models.ForeignKey(TWUser, related_name="favorite_tweets")
    value = models.ForeignKey(Tweet, related_name='favorited_by')
    ended = models.DateTimeField(null=True)

def get_from_any_or_create(table, **kwargs):
    '''
    Retrieve an object from any of the attributes. If any attribute in <kwargs> matches an entry in <table>, then the
    entry is returned, otherwise an object is created using all the attributes.
    '''
    kwargs = {kwarg : kwargs[kwarg] for kwarg in kwargs.keys() if kwargs[kwarg]} # eliminate "None" values
    item = None
    for param in kwargs.keys():
        if not item:
            try:
                item = table.objects.get(**{param:kwargs[param]})
            except models.ObjectDoesNotExist:
                continue
            except:
                log("An error occured in get_from_any_or_create(%s)"%kwargs)
        else:
            setattr(item, param, kwargs[param])
    if item:
        item.save()
        return item, False
    else:
        try:
            item = table.objects.create(**kwargs)
        except IntegrityError: # sometimes the table entry is created while this processes...
            log("django.db.utils.IntegrityError caugth!")
            return get_from_any_or_create(table, **kwargs)
        return item, True

