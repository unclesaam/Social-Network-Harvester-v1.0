from django.db import models
from django.db.utils import IntegrityError
from django.core.exceptions import MultipleObjectsReturned
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

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifier",
                "description": "Identifier number of the Place object"},
            "attributes": {
                "name": "Attributes",
                "description": "(Composite) All values not explicitely stored in the Aspira's database"},
            "bounding_box": {
                "name": "Bounding box",
                "description": "Imaginary geographiqual square bounding the Place object"},
            "country": {
                "name": "Country",
                "description": "Coutry of the Place"},
            "full_name": {
                "name": "Full Name",
                "description": "Full arbitrary name of the Place"},
            "name": {
                "name": "Name",
                "description": "Short arbitrary name (or abbreviation) of the Place"},
            "place_type": {
                "name": "Place type",
                "description": "Type of the Place"},
            "url": {
                "name": "Url",
                "description": "Url associated with the Place object"}
        }

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

    def get_fields_description(self):
        return {
            "term": {
                "name": "Term",
                "description": "Hashtag word, or term to be searched for"},
            "hit_count": {
                "name": "Hit count",
                "description": "Total number of Tweet in the current database containing the hashtag"
            }

        }

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


    def get_fields_description(self):
        return {
            "_harvest_since": {
                "name": "Harvest since",
                "description": "Date of begining of the harvest"},
            "_harvest_until": {
                "name": "Harvest until",
                "description": "Date of end of the harvest"},
            "_has_reached_begining":{
                'name':'Harvest completed',
                'description':'Whether or not the harvest has completed'},
            '_last_harvested':{
                'name':'Last harvested',
                'description':'Date of the last harvest of this Hashtag'},
            'harvest_count':{
                'name':'Harvest count',
                'description':'Number of Tweets in the current database harvested by this search'}
        }

    def __str__(self):
        since = "undefined"
        until = "undefined"
        if self._harvest_since :
            since = "%s-%s-%s"%(self._harvest_since.year, self._harvest_since.month, self._harvest_since.day)
        if self._harvest_until :
            until = "%s-%s-%s" % (self._harvest_until.year, self._harvest_until.month, self._harvest_until.day)
        return "#%s's harvester (%s to %s)" %(self.hashtag.term, since, until)

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
    profile_image_url= models.CharField(max_length=1024)
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

    def get_fields_description(self):
        return {
            "screen_name": {
                "description": "Identifier name of the user's account.",
                "name": "Screen Name"},
            "name": {
                "description": "Full name of the user.",
                "name": "Name"},
            "_ident": {
                "description": "Identifier number of the account.",
                "name": "Identifier"},
            "created_at": {
                "description": "Time of creation of the account.",
                "name": "Created at"},
            "geo_enabled": {
                "description": "(Boolean) Whether the account as geo-location enabled.",
                "name": " Geo-Enabled"},
            "has_extended_profile": {
                "description": "(Boolean) Whether or not the account has an extended profile.",
                "name": "Extended Profile"},
            "is_translator": {
                "description": "(Boolean) Whether or not the user is part of the Twitter's translators community.",
                "name": "Is Translator"},
            "lang": {
                "description": "Primary language of the account.",
                "name": "Language"},
            "location": {
                "description": "Geolocation of the user. May not be a exact field as users choose what they write.",
                "name": "Location"},
            "protected": {
                "description": "(Boolean) Whether or not the user allows his account to be harvested via the Twitter API.",
                "name": "Protected"},
            "verified": {
                "description": "(Boolean) Whether or not the account has been authenticated as legitimate by the Twitter staff.",
                "name": "Verified"},
            "time_zone": {
                "description": "Time zone of the account location.",
                "name": "Time Zone"},
            "url": {
                "description": "Website of the user, or organisation.",
                "name": "URL"},
            "description": {
                "description": "Description of the account.",
                "name": "Description"},
            "statuses_count": {
                "description": "Number of statuses as of the last harvest.",
                "name": "Statuses count"},
            "favourites_count": {
                "description": "Number of favorite Tweets as of the last harvest.",
                "name": "Favorite count"},
            "followers_count": {
                "description": "Number of followers of the account as of the last harvest.",
                "name": "Followers count"},
            "friends_count": {
                "description": "Number of accounts followed by this user as of the last harvest.",
                "name": "Friends count"},
            "listed_count": {
                "description": "Number of Twitter's public lists that the user is part of.",
                "name": "Listed count"}
        }

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
            return 'Empty TWUser'

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
                if not lastItem or lastItem.recorded_time != today():
                    if atr == 'url':
                        # having a class named "url" breaks the Django import system.
                        className = TWUrl
                    else:
                        className = globals()[atr]
                    newItem = className(twuser=self, value=jObject[atr])
                    try:
                        newItem.save()
                    except:
                        log('className: %s'% atr)
                        raise
                elif lastItem.value != jObject[atr]:
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
    def get_fields_description(self):
        val = super(follower, self).get_fields_description()
        val.update({
            'ended': {
                'name': 'Ended',
                'description': 'Time at wich the Twitter user has stop following the target user'},
            'recorded_time': {
                'name': 'Recorded Time',
                'description': 'Time at wich the "following" relationship has been recorded'}
        })
        pretty(val)
        return val


############### TWEET ####################

class Tweet(models.Model):
    class Meta:
        app_label = "Twitter"

    def __str__(self):
        return "%s tweet #%s"%(("@%s"%self.user if self.user else 'unidentifed TWUser'), self._ident)

    def get_obj_ident(self):
        return "Tweet__%s" % self.pk

    def get_ident(self):
        return self._ident

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

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifier",
                "description": "Identifier number of the Tweet"},
            "coordinates": {
                "name": "Coordinates",
                "description": "Geographic position of the Tweet's emmission"},
            "contributors": {
                "name": "Contributors",
                "description": "Twitter users who contributed to the Tweet. By posting or editing"},
            "created_at": {
                "name": "Created at",
                "description": "Date and time of the Tweet's posting"},
            "deleted_at": {
                "name": "Deleted at",
                "description": "Date and time of the Tweet's deletion, if any"},
            "text": {
                "name": "Text",
                "description": "Main content of the Tweet"},
            "retweet_count": {
                "name": "Retweet count",
                "description": "Latest value of the number of retweets"},
            "possibly_sensitive": {
                "name": "Possibly sensitive",
                "description": "(Boolean) Determines if the Tweet could be interpreted as offensive to some audience"},
            "place": {
                "name": "Place",
                "description": "Place(s) of emission of the Tweet"},
            "source": {
                "name": "Source",
                "description": "Application used to post the Tweet"},
            "lang": {
                "name": "Language",
                "description": "Language of the text"},
            "withheld_copyright": {
                "name": "Witheld copyright",
                "description": "(Boolean) Whether the Tweet contains copyrighted material"},
            "withheld_in_countries": {
                "name": "Witheld in countries",
                "description": "Countries in which the Tweet is witheld from appearing"},
            "withheld_scope": {
                "name": "Witheld scope",
                "description": "The extent of wich the Tweet if witheld in some countries"},
            "user": {
                "name": "User",
                "description": "Twitter user who innitially posted the Tweet"},
            "in_reply_to_user": {
                "name": "In reply to user",
                "description": "Twitter user to wich the Tweet is intended, if any"},
            "in_reply_to_status": {
                "name": "In reply to Status ",
                "description": "Tweet to wich the Tweet is intended, if any"},
            "quoted_status": {
                "name": "Quoted status",
                "description": "Tweet quoted in the text, if any"},
            "retweet_of": {
                "name": "Retweet of",
                "description": "Original Tweet, to wich a retweet has been posted"},
            "userMentionsList": {
                "name": "User mentions",
                "description": "Twitter users mentionned in the text"},
            "hashtagsList": {
                "name":"Hashtags",
                "description": "Hashtags contained in the text"},
        }

    def hashtagsList(self):
        return ["#%s"%hashtag.term for hashtag in self.hashtags.all()]

    def userMentionsList(self):
        return ["@%s" % user.screen_name for user in self.user_mentions.all()]

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
        try:
            twuser, new = get_from_any_or_create(TWUser, _ident=ident, screen_name=screen_name)
        except TWUser.MultipleObjectsReturned:
            twusers = TWUser.objects.filter(_ident=ident, screen_name=screen_name)
            if len(twusers) > 2 :
                raise Exception('%s objects returned for TWUser %s!'%(len(twusers),(
                ident, screen_name)))
            twuser = joinTWUsers(twusers[0], twusers[1])
        self.user = twuser

    def setInReplyToStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.in_reply_to_status = tweet

    def setInReplyToUser(self, **kwargs):
        try:
            twuser, new = get_from_any_or_create(TWUser, **kwargs)
        except TWUser.MultipleObjectsReturned:
            twusers = TWUser.objects.filter(**kwargs)
            if len(twusers) > 2:
                raise Exception('%s objects returned for TWUser %s!' % (len(twusers), (
                    ident, screen_name)))
            twuser = joinTWUsers(twusers[0], twusers[1])
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
                if not lastItem or lastItem.recorded_time != today():
                    className = globals()[atr]
                    newItem = className(tweet=self, value=jObject[atr])
                    newItem.save()
                elif lastItem.value != jObject[atr]:
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
                try:
                    twUser, new = get_from_any_or_create(TWUser, _ident=id, screen_name=screen_name)
                except TWUser.MultipleObjectsReturned:
                    twUsers = TWUser.objects.filter(_ident=id, screen_name=screen_name)
                    if len(twUsers) > 2:
                        raise Exception('%s objects returned for TWUser %s!' % (len(twUsers), (
                            ident, screen_name)))
                    twUser = joinTWUsers(twUsers[0], twUsers[1])
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

    def get_fields_description(self):
        val = super(favorite_tweet, self).get_fields_description()
        val.update({
            'ended':{
                'name': 'Ended',
                'description':'Time at wich the TWuser no longer favorites the target Tweet'
            },
            'recorded_time':{
                'name':'Recorded Time',
                'description':'Time at wich the target Tweet has been recorded as a favorite of the Twitter user'
            }
        })
        return val

def get_from_any_or_create(table, **kwargs):
    '''
    Retrieves an object from any of the attributes. If any attribute in <kwargs> matches an entry in <table>, then the
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
                log("An error occured in get_from_any_or_create(%s) (Twitter.models)"%kwargs)
                raise
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

@twitterLogger.debug(showArgs=True)
def joinTWUsers(user1, user2):
    if user2.screen_name:
        user1.screen_name = user2.screen_name
    if user2._ident:
        user1._ident = user2._ident
    for label in [
        'screen_names',
        'names',
        'time_zones',
        'urls',
        'descriptions',
        'statuses_counts',
        'favourites_counts',
        'followers_counts',
        'friends_counts',
        'listed_counts',
    ]:
        log('transfering all %s from %s to %s'%(label,user2,user1))
        for item in getattr(user, label).all():
            item.twuser = user1
            item.save()
    user1.save()
    user2.delete()
    return user1

