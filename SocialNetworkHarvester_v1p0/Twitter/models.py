from django.db import models
from django.db.utils import IntegrityError
from django.core.exceptions import MultipleObjectsReturned
import _mysql_exceptions
from SocialNetworkHarvester_v1p0.models import *
from django.utils.timezone import utc
import json
from datetime import datetime
import re, time

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
                "description": "Identifier number of the Place object",
                "type": "short_string"},
            "attributes": {
                "name": "Attributes",
                "description": "(Composite) All values not explicitely stored in the Aspira's database",
                "type": "long_string"},
            "bounding_box": {
                "name": "Bounding box",
                "description": "Imaginary geographiqual square bounding the Place object",
                "type": "short_string"},
            "country": {
                "name": "Country",
                "description": "Coutry of the Place",
                "type": "short_string"},
            "full_name": {
                "name": "Full Name",
                "description": "Full arbitrary name of the Place",
                "type": "short_string"},
            "name": {
                "name": "Name",
                "description": "Short arbitrary name (or abbreviation) of the Place",
                "type": "short_string"},
            "place_type": {
                "name": "Place type",
                "description": "Type of the Place",
                "type": "short_string"},
            "url": {
                "name": "Url",
                "description": "Url associated with the Place object",
                "type": "link_url"}
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
                "name": "Terme",
                "description": "Mot ou terme du hastag. Sujet de la recherche",
                "type": "short_string"},
            "hit_count": {
                "name": "Nombre de tweets",
                "description": "Nombre total de tweets dans la base de données contenant ce hashtag.",
                "type": "integer"
            }

        }

    def getLink(self):
        return "/twitter/hashtag/%s"%self.pk

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
                "name": "Collecte depuis",
                "description": "Date de début de la collecte (collecte les tweets émis après la date)",
                "type": "date",
                "options":{
                    "admin_only":False,
                }},
            "_harvest_until": {
                "name": "Collecte jusqu'à",
                "description": "Date de fin de la collecte (collecte les tweets émis avant la date)",
                "type": "date",
                "options":{
                    "admin_only":False,
                }},
            "_has_reached_begining":{
                'name':'Collecte complétée',
                'description':'Si la collecte est complétée pour la période spécifiée',
                "type": "boolean",
                "options":{
                    "admin_only":False,
                }},
            '_last_harvested':{
                'name':'Dernière collecte',
                'description':'Date de la dernière collecte pour ce hashtag',
                "type": "date",
                "options":{
                    "admin_only":False,
                }},
            'harvest_count':{
                'name':'Nombre de résultats',
                'description':'Nombre de tweets dans la base de données qui furent ajoutées suite à la recherche de ce hashtag',
                "type": "integer"}
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
    screen_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
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
    def last_updated(self):return self._last_updated
    _last_tweet_harvested = models.DateTimeField(null=True)
    def last_tweet_harvested(self):return self._last_tweet_harvested
    _last_friends_harvested = models.DateTimeField(null=True)
    def last_friends_harvested(self):return self._last_friends_harvested
    _last_followers_harvested = models.DateTimeField(null=True)
    def last_followers_harvested(self):return self._last_followers_harvested
    _last_fav_tweet_harvested = models.DateTimeField(null=True)
    def last_fav_tweet_harvested(self):return self._last_fav_tweet_harvested
    _error_on_update = models.BooleanField(default=False)
    def error_on_update(self):return self._error_on_update
    _has_duplicate = models.BooleanField(default=False)
    def has_duplicate(self):return self._has_duplicate
    _error_on_harvest = models.BooleanField(default=False)
    def error_on_harvest(self):return self._error_on_harvest
    _error_on_network_harvest = models.BooleanField(default=False)
    def error_on_network_harvest(self):return self._error_on_network_harvest
    _update_frequency = models.IntegerField(default=5) # 1 = every day, 2 = every 2 days, etc.
    def update_frequency(self):return self._update_frequency
    _harvest_frequency = models.IntegerField(default=1)
    def harvest_frequency(self):return self._harvest_frequency
    _network_harvest_frequency = models.IntegerField(default=1)
    def network_harvest_frequency(self):return self._network_harvest_frequency
    _has_reached_begining = models.BooleanField(default=False)
    def has_reached_begining(self):return self._has_reached_begining


    def get_fields_description(self):
        return {
            "screen_name": {
                "description": "Nom d'utilisateur, identifiant le compte.",
                "name": "Nom d'utilisateur",
                "type":"short_string"},
            "name": {
                "description": "Nom complet de l'utilisateur.",
                "name": "Nom",
                "type":"short_string"},
            "_ident": {
                "description": "Numéro-identifiant du compte.",
                "name": "Identifiant",
                "type":"short_string"},
            "created_at": {
                "description": "Temps de création du compte.",
                "name": "Créé le",
                "type":"date"},
            "geo_enabled": {
                "description": "(Booléen) Si le compte a activé la géo-localisation.",
                "name": "Geo-Activé",
                "type":"boolean"},
            "has_extended_profile": {
                "description": "(Booléen) Si le compte a un profil étendu.",
                "name": "Profil Étendu",
                "type":"boolean"},
            "is_translator": {
                "description": "(Booléen) Si l'utilisateur du compte fait partie de la communauté des traducteurs Twitter.",
                "name": "Est Traducteur",
                "type":"boolean"},
            "lang": {
                "description": "Langue première du compte.",
                "name": "Language",
                "type":"short_string"},
            "location": {
                "description": "Géo-location de l'utilisateur du compte. Peut ne pas être exact puisque les utilisateurs choisissent ce qu'ils écrivent.",
                "name": "Location",
                "type":"short_string"},
            "protected": {
                "description": "(Booléen) Si le compte dénie la collecte de ses informations via l'API de Twitter",
                "name":"Protégé",
                "type":"boolean",
                "options":{
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }
            },
            "verified": {
                "description": "(Booléen) Si le compte as été vérifié comme légitime par un employé de Twitter.",
                "name": "Verifié",
                "type":"boolean",
                "options": {
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'red',
                            True: "green"
                        }
                    }
                }
            },
            "time_zone": {
                "description": "Fuseau horaire principal du compte.",
                "name": "Fuseau horaire",
                "type":"short_string"},
            "url": {
                "description": "Site web de l'utilisateur ou de l'organisation.",
                "name": "URL",
                "type":"link_url"},
            "description": {
                "description": "Description du compte, de l'utilisateur ou de l'organisation.",
                "name": "Description",
                "type":"long_string"},
            "statuses_count": {
                "description": "Nombre de status en date de la dernière collecte (généralement <24h).",
                "name": "Nombre de status",
                "type":"integer"},
            "favourites_count": {
                "description": "Nombre de tweets favoris en date de la dernière collecte (généralement <24h).",
                "name": "Nombre de favoris",
                "type":"integer"},
            "followers_count": {
                "description": "Nombre d'abonnés (followers) au compte en date de la dernière collecte (généralement <24h).",
                "name": "Nombre d'abonnés",
                "type":"integer"},
            "friends_count": {
                "description": "Nombre de compte suivi par l'utilisateur en date de la dernière collecte.",
                "name": "Nombre d'abonnements",
                "type":"integer"},
            "listed_count": {
                "description": "nombre de listes publiques dans lesquelles le compte apparait.",
                "name": "Mentions publiques",
                "type":"integer"
            },
            "profile_image_url": {
                "description": "Url de l'image de profil de l'utilisateur (au moment de la dernière collecte).",
                "name": "Image de profil",
                "type":"image_url",
                "options":{
                    "render":lambda value: re.sub("_normal","",value),
                }
            },
            "_last_updated":{
                "name":"Last updated",
                "type":"date",
                "options":{
                    "admin_only":True
                }},
            "_last_tweet_harvested":{
                "name":"Last tweet-harvested",
                "type":"date",
                "options":{
                    "admin_only":True
                }},
            "_last_friends_harvested":{
                "name":"Last-friend-harvested",
                "type":"date",
                "options":{
                    "admin_only":True
                }},
            "_last_followers_harvested":{
                "name":"Last followers-harvested",
                "type":"date",
                "options":{
                    "admin_only":True
                }},
            "_last_fav_tweet_harvested":{
                "name":"Last fav-tweet-harvested",
                "type":"date",
                "options":{
                    "admin_only":True
                }},
            "_error_on_update":{
                "name":"Error on update",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_has_duplicate":{
                "name":"Has duplicate",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_error_on_harvest":{
                "name":"Error on harvest",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_error_on_network_harvest":{
                "name":"Error on network-harvest",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                    "tile_style": {
                        "value_text_coloring": {
                            False: 'green',
                            True: "red"
                        }
                    }
                }},
            "_update_frequency":{
                "name":"Update frequency",
                "type":"integer",
                "options":{
                    "admin_only":True
                }},
            "_harvest_frequency":{
                "name":"Harvest frequency",
                "type":"integer",
                "options":{
                    "admin_only":True,
                }},
            "_network_harvest_frequency":{
                "name":"Network-harvest frequency",
                "type":"integer",
                "options":{
                    "admin_only":True
                }},
            "_has_reached_begining":{
                "name":"Has reached begining",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                    "tile_style":{
                        "value_text_coloring": {
                            False:'blue',
                            True:"green"
                        }
                    }
                }},
        }

    class Meta:
        app_label = "Twitter"

    def getLink(self):
        return "/twitter/user/%s"%self.pk

    def get_obj_ident(self):
        return "TWUser__%s" % self.pk

    def __str__(self):
        if self.screen_name:
            return self.screen_name
        else:
            return 'TWUser %s'%self._ident


    def __init__(self, *args, **kwargs):
        super(TWUser, self).__init__(*args, **kwargs)
        if 'jObject' in kwargs: self.UpdateFromResponse(kwargs['jObject'])

    def biggerImageUrl(self):
        return re.sub("_normal.","_bigger.",self.profile_image_url)


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
    value = models.ForeignKey(TWUser, related_name='friends') # "value" user is following "twuser", calls it it's "friend"
    ended = models.DateTimeField(null=True)
    def get_fields_description(self):
        val = super(follower, self).get_fields_description()
        val.update({
            'ended': {
                'name': 'Terminé',
                'description': "Date à l'aquelle l'utilisateur Twitter a cessé de suivre l'utilisateur-cible"},
            'recorded_time': {
                'name': 'Temps d\'enregistrement',
                'description': 'Temps auquel la relation as été enregistrée'}
        })
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
    def last_updated(self):return self._last_updated
    _last_retweeter_harvested = models.DateTimeField(null=True)
    def last_retweeter_harvested(self):return self._last_retweeter_harvested
    _error_on_update = models.BooleanField(default=False)
    def error_on_update(self):return self._error_on_update
    _error_on_retweet_harvest = models.BooleanField(default=False)
    def error_on_retweet_harvest(self):return self._error_on_retweet_harvest

    _date_time_fields = ['created_at']
    _time_labels = ['retweet_count']
    _relationals = ['place_id','in_reply_to_user_id','in_reply_to_status_id','quoted_status_id','retweet_of_id',
                    'user_id', 'hashtags_id']

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "Nombre identificateur du tweet",
                "type":"short_string"},
            "coordinates": {
                "name": "Coordonnées",
                "description": "Coordonnées géographiques du tweet",
                "type":"short_string"},
            "contributors": {
                "name": "Contributeurs",
                "description": "Utilisateurs Twitter ayant contribué au tweet, en postant ou en éditant",
                "type":"object_list"},
            "created_at": {
                "name": "Création",
                "description": "Date et heure de publication du tweet",
                "type":"date"},
            "deleted_at": {
                "name": "Effacement",
                "description": "Date et heure d'effacement du tweet, si applicable",
                "type":"date"},
            "text": {
                "name": "Texte",
                "description": "Contenu textuel du tweet",
                "type":"long_string"},
            "retweet_count": {
                "name": "Nombre de retweets",
                "description": "Dernière valeur enregistrée du nombre de retweets",
                "type":"integer"},
            "possibly_sensitive": {
                "name": "Possiblement sensible",
                "description": "(Booléen) Si le tweet pourrait être perçu comme offensant par un certain auditoire",
                "type":"boolean"},
            "place": {
                "name": "Place",
                "description": "Place(s) d'émission du tweet",
                "type":"short_string"},
            "source": {
                "name": "Source",
                "description": "Application utilisée pour publier le tweet",
                "type":"html_link"},
            "lang": {
                "name": "Language",
                "description": "Language du texte du tweet",
                "type":"short_string"},
            "withheld_copyright": {
                "name": "Droits d'auteurs",
                "description": "(Booléen) Si le tweet contient du matériel protégé par des droits d'auteurs",
                "type":"boolean"},
            "withheld_in_countries": {
                "name": "Retenu dans pays",
                "description": "Pays dans lesquels le tweet est masqué et n'apparait pas aux utilisateurs",
                "type":"short_string"},
            "withheld_scope": {
                "name": "Étendue de retenue",
                "description": "L'étendue de la politique de retenue si le tweet est masqué dans certains pays",
                "type":"short_string"},
            "user": {
                "name": "Auteur",
                "description": "Utilisateur Twitter ayant publié le tweet",
                "type":"object"},
            "in_reply_to_user": {
                "name": "En réponse à l'utilisateur",
                "description": "Utilisateur Twitter à qui le tweet répond, si applicable",
                "type":"object"},
            "in_reply_to_status": {
                "name": "En réponse au status",
                "description": "Tweet envers lequel le tweet répond, si applicable",
                "type":"object"},
            "quoted_status": {
                "name": "Status cité",
                "description": "Tweet cité dans le tweet. Différent d'un retweet.",
                "type":"object"},
            "retweet_of": {
                "name": "Retweet de",
                "description": "Tweet original du retweet, si applicable",
                "type":"object"},
            "userMentionsList": {
                "name": "Utilisateurs mentionnés",
                "description": "Utilisateurs Twitter mentionnés dans le texte",
                "type":"long_string",
                "options":{"displayable":False}},
            "hashtagsList": {
                "name":"Hashtags",
                "description": "Hashtags contenus dans le texte",
                "type":"long_string",
                "options":{"displayable":False}},
            "user_mentions": {
                "name": "Utilisateurs mentionnés",
                "description": "Utilisateurs Twitter mentionnés dans le texte",
                "type":"object_list",
                "options":{"downloadable":False}},
            "hashtags": {
                "name":"Hashtags",
                "description": "Hashtags contenus dans le texte",
                "type":"object_list",
                "options":{"downloadable":False}},
            "_last_updated":{
                "name":"Last updated",
                "type":"date",
                "options":{
                    "admin_only":True,
                }
            },
            "_last_retweeter_harvested":{
                "name":"Last retweet-harvested",
                "type":"date",
                "options":{
                    "admin_only":True,
                }
            },
            "_error_on_update":{
                "name":"Error on update",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                }
            },
            "_error_on_retweet_harvest":{
                "name":"Error on retweet-harvest",
                "type":"boolean",
                "options":{
                    "admin_only":True,
                }
            },
        }

    def getLink(self):
        return "/twitter/tweet/%s"%self.pk

    def _truncated_text(self, n):
        if self.text:return self.text[:n] + '...' * (len(self.text) > n)
    def truncated_text_25(self):return self._truncated_text(25)
    def truncated_text_50(self):return self._truncated_text(50)
    def truncated_text_100(self):return self._truncated_text(100)

    def hashtagsList(self):
        return ["#%s"%hashtag.term for hashtag in self.hashtags.all()]

    def userMentionsList(self):
        return ["@%s" % user.screen_name for user in self.user_mentions.all()]

    def digestSource(self):
        if self.source:
            return {
                "name":re.match(r"<a.*>(?P<name>.*)</a>", self.source).group("name"),
                "url": re.match(r'.*href="(?P<url>[^"]+)"', self.source).group("url")
            }

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
        except:
            doubles = TWUser.objects.filter(screen_name=screen_name)
            doubles[0]._has_duplicate = True
            doubles[0].save()
            log('TWUSER %s HAS %s DUPLICATES!'%(doubles[0], doubles.count()-1))
            raise
            #twusers = TWUser.objects.filter(_ident=ident, screen_name=screen_name)
            #twuser = joinTWUsers(twusers[0], twusers[1])
        self.user = twuser

    def setInReplyToStatus(self, twid):
        tweet, new = Tweet.objects.get_or_create(_ident=twid)
        self.in_reply_to_status = tweet

    def setInReplyToUser(self, **kwargs):
        try:
            twuser, new = get_from_any_or_create(TWUser, **kwargs)
        except:
            log('kwargs: %s'%kwargs)
            doubles = TWUser.objects.filter(**kwargs)
            doubles[0]._has_duplicate = True
            doubles[0].save()
            log('TWUSER %s HAS %s DUPLICATES!' % (doubles[0], doubles.count() - 1))
            time.sleep(3)
            raise
            #twusers = TWUser.objects.filter(**kwargs)
            #twuser = joinTWUsers(twusers[0], twusers[1])
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
                twUser, new = get_from_any_or_create(TWUser, _ident=user_mention['id'])
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
            except MultipleObjectsReturned:
                log('MULTIPLE OBJECTS RETURNED!')
                pretty(kwargs)
                log(table.objects.filter(**{param: kwargs[param]}))
                log("Returning first instance of item")
                item = table.objects.filter(**{param:kwargs[param]}).first()
            except:
                log("An unknown error occured in get_from_any_or_create(%s) (Twitter.models)"%kwargs)
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

#@twitterLogger.debug(showArgs=True)
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

