from django.db import models
from SocialNetworkHarvester_v1p0.models import Integer_time_label, Big_integer_time_label, Image_time_label, time_label

from SocialNetworkHarvester_v1p0.settings import youtubeLogger, DEBUG
log = lambda s: youtubeLogger.log(s) if DEBUG else 0
pretty = lambda s: youtubeLogger.pretty(s) if DEBUG else 0
logerror = lambda s: youtubeLogger.exception(s)
from Youtube.management.commands.harvest.queues import *
import re

from datetime import datetime
from django.utils.timezone import utc
today = lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)


####################### YTCHANNEL  #######################

class YTChannel(models.Model):
    _ident = models.CharField(max_length=128,null=True)
    userName = models.CharField(max_length=32, null=True)
    description = models.CharField(max_length=8192, null=True)
    keywords = models.CharField(max_length=1000, null=True)
    profileColor = models.CharField(max_length=16, null=True)
    title = models.CharField(max_length=512, null=True)
    publishedAt = models.DateTimeField(null=True)
    hiddenSubscriberCount = models.BooleanField(default=False)
    isLinked = models.BooleanField(default=False)
    privacyStatus = models.CharField(max_length=32, null=True)
    featuredChannel = models.ManyToManyField('self',related_name='featured_by')
    commentCount = models.BigIntegerField(null=True)
    subscriberCount = models.BigIntegerField(null=True)
    videoCount = models.IntegerField(null=True)
    viewCount = models.BigIntegerField(null=True)

    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _last_video_harvested = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _error_on_harvest = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1)  # 1 = every day, 2 = every 2 days, etc.
    _harvest_frequency = models.IntegerField(default=1)
    _has_reached_begining = models.BooleanField(default=False)
    _error_on_comment_harvest = models.BooleanField(default=False)
    _last_comment_harvested = models.DateTimeField(null=True)
    _earliest_comment_page_token = models.CharField(max_length=128,null=True)
    _has_reached_comments_begining = models.BooleanField(default=False)
    _last_subs_harvested = models.DateTimeField(null=True)
    _public_subscriptions = models.BooleanField(default=True)
    _last_playlists_harvested = models.DateTimeField(null=True)


    basicFields = {
        '_ident':                   ['id'],
        'description':              ['brandingSettings','channel','description'],
        'keywords':                 ['brandingSettings','channel','keywords'],
        'profileColor':             ['brandingSettings','channel','profileColor'],
        'title':                    ['brandingSettings','channel','title'],
        'isLinked':                 ['status', 'isLinked'],
        'privacyStatus':            ['status', 'privacyStatus'],
        'hiddenSubscriberCount':    ['statistics', 'hiddenSubscriberCount'],
        'commentCount':             ['statistics', 'commentCount'],
        'subscriberCount':          ['statistics', 'subscriberCount'],
        'videoCount':               ['statistics', 'videoCount'],
        'viewCount':                ['statistics', 'viewCount'],
    }
    dateTimeFields = {
        'publishedAt':              ['snippet','publishedAt'],
    }
    statistics = {
        'comment_counts':           ['statistics','commentCount'],
        'subscriber_counts':        ['statistics','subscriberCount'],
        'video_counts':             ['statistics','videoCount'],
        'view_counts':              ['statistics','viewCount'],
    }


    class Meta:
        app_label = "Youtube"

    def __str__(self):
        if self.title: return self.title
        if self.userName: return self.userName
        if self._ident: return "channel #%s"%self._ident
        return 'Unidentified YTChannel'

    def get_fields_description(self):
        return {
            '_ident':{
                'name':'Identifiant',
                'description':'Identifiant unique de la chaîne'
            },
            'description': {
                'name': 'Description',
                'description': 'Description du type de contenu de la chaîne'
            },
            'keywords': {
                'name': 'Mot-clefs',
                'description': 'Mots-clefs associés à la chaîne'
            },
            'profileColor': {
                'name': 'Couleur de profil',
                'description': 'Couleur de fond de la chaîne'
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre de la chaîne'
            },
            'userName': {
                'name': 'Nom d\'utilisateur',
                'description': 'Nom unique de la chaîne. Peut être changé durant l\'existence de la chaîne. Non-permanent'
            },
            'publishedAt': {
                'name': 'Création',
                'description': 'Date de création de la chaîne'
            },
            'hiddenSubscriberCount': {
                'name': 'Nombre d\'abonnés caché',
                'description': 'Détermine si le nombre d''abonnés à la chaine est privé ou public'
            },
            'isLinked': {
                'name': 'Liaison Google+',
                'description': 'Détermine si la chaîne est reliée à un compte Google+'
            },
            'privacyStatus': {
                'name': 'Confidentialité',
                'description': 'Status de confidentialité de la chaîne. Peut être "Private", "Public" or "Unlisted"'
            },
            'featuredChannel': {
                'name': 'Chaînes présentées',
                'description': 'Autres chaînes mises en vedette par la chaîne'
            },
            'commentCount': {
                'name': 'Nombre de commentaires',
                'description': 'Nombre de commentaires postés sur la page "discussion" de la chaîne (au moment de la dernière mise à jour)'
            },
            'subscriberCount': {
                'name': 'Nombre d''abbonés',
                'description': 'Nombre d''abonnés à la chaîne (au moment de la dernière mise à jour)'
            },
            'videoCount': {
                'name': 'Nombre de vidéos',
                'description': 'Nombre de vidéos postés sur la chaîne (au moment de la dernière mise à jour)'
            },
            'viewCount': {
                'name': 'Nombre de vues',
                'description': 'Nombre combiné de vues de toutes les vidéos postés par la chaîne (au moment de la dernière mise à jour)'
            },
        }

    def get_obj_ident(self):
        return "YTChannel__%s" % self.pk

    def ident(self):
        return self._ident

    #@youtubeLogger.debug(showArgs=False)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')
        #pretty(jObject)
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateImages(jObject)
        self._last_updated = today()
        self.save()

    #@youtubeLogger.debug(showArgs=True)
    def copyBasicFields(self, jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    setattr(self, attr, val)

    #@youtubeLogger.debug()
    def copyDateTimeFields(self,jObject):
        for attr in self.dateTimeFields:
            if self.dateTimeFields[attr][0] in jObject:
                val = jObject[self.dateTimeFields[attr][0]]
                for key in self.dateTimeFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
                    val = val.replace(tzinfo=utc)
                    setattr(self, attr, val)

    #@youtubeLogger.debug()
    def updateStatistics(self,jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    pass
                    #log('Invalid dict sequence: %s'%self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(channel=self,value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(channel=self,value=val)




    #@youtubeLogger.debug()
    def updateImages(self,jObject):
        #TODO: Save a copy of the images on disk
        pass


# OBJECT SAMPLE. MORE AT https://developers.google.com/youtube/v3/docs/channels
'''
{
  "kind": "youtube#channel",
  "etag": etag,
  "id": string,
  "snippet": {
    "title": string,
    "description": string,
    "customUrl": string,
    "publishedAt": datetime,
    "thumbnails": {
      (key): {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
      }
    },
    "defaultLanguage": string,
    "localized": {
      "title": string,
      "description": string
    },
    "country": string
  },
  "contentDetails": {
    "relatedPlaylists": {
      "likes": string,
      "favorites": string,
      "uploads": string,
      "watchHistory": string,
      "watchLater": string
    }
  },
  "statistics": {
    "viewCount": unsigned long,
    "commentCount": unsigned long,
    "subscriberCount": unsigned long,
    "hiddenSubscriberCount": boolean,
    "videoCount": unsigned long
  },
  "topicDetails": {
    "topicIds": [
      string
    ]
  },
  "status": {
    "privacyStatus": string,
    "isLinked": boolean,
    "longUploadsStatus": string
  },
  "brandingSettings": {
    "channel": {
      "title": string,
      "description": string,
      "keywords": string,
      "defaultTab": string,
      "trackingAnalyticsAccountId": string,
      "moderateComments": boolean,
      "showRelatedChannels": boolean,
      "showBrowseView": boolean,
      "featuredChannelsTitle": string,
      "featuredChannelsUrls": [
        string
      ],
      "unsubscribedTrailer": string,
      "profileColor": string,
      "defaultLanguage": string,
      "country": string
    },
    "watch": {
      "textColor": string,
      "backgroundColor": string,
      "featuredPlaylistId": string
    },
    "image": {
      "bannerImageUrl": string,
      "bannerMobileImageUrl": string,
      "watchIconImageUrl": string,
      "trackingImageUrl": string,
      "bannerTabletLowImageUrl": string,
      "bannerTabletImageUrl": string,
      "bannerTabletHdImageUrl": string,
      "bannerTabletExtraHdImageUrl": string,
      "bannerMobileLowImageUrl": string,
      "bannerMobileMediumHdImageUrl": string,
      "bannerMobileHdImageUrl": string,
      "bannerMobileExtraHdImageUrl": string,
      "bannerTvImageUrl": string,
      "bannerTvLowImageUrl": string,
      "bannerTvMediumImageUrl": string,
      "bannerTvHighImageUrl": string,
      "bannerExternalUrl": string
    },
    "hints": [
      {
        "property": string,
        "value": string
      }
    ]
  },
  "invideoPromotion": {
    "defaultTiming": {
      "type": string,
      "offsetMs": unsigned long,
      "durationMs": unsigned long
    },
    "position": {
      "type": string,
      "cornerPosition": string
    },
    "items": [
      {
        "id": {
          "type": string,
          "videoId": string,
          "websiteUrl": string,
          "recentlyUploadedBy": string
        },
        "timing": {
          "type": string,
          "offsetMs": unsigned long,
          "durationMs": unsigned long
        },
        "customMessage": string,
        "promotedByContentOwner": boolean
      }
    ],
    "useSmartTiming": boolean
  },
  "auditDetails": {
    "overallGoodStanding": boolean,
    "communityGuidelinesGoodStanding": boolean,
    "copyrightStrikesGoodStanding": boolean,
    "contentIdClaimsGoodStanding": boolean
  },
  "contentOwnerDetails": {
    "contentOwner": string,
    "timeLinked": datetime
  },
  "localizations": {
    (key): {
      "title": string,
      "description": string
    }
  }
}
'''


class SubscriberCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriber_counts')
class VideoCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='video_counts')
class Subscription(time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriptions')
    value = models.ForeignKey(YTChannel, related_name='subscribers')
    ended = models.DateTimeField(null=True)

#######################  YTVIDEO  ########################

class YTVideo(models.Model):
    #basic fields
    _ident = models.CharField(max_length=128, null=True)
    channel = models.ForeignKey(YTChannel, related_name='videos')
    publishedAt = models.DateTimeField(null=True)
    title = models.CharField(max_length=128,null=True)
    description = models.CharField(max_length=8192,null=True)
    contentRating_raw = models.CharField(max_length=2048, null=True)
    privacyStatus = models.CharField(max_length=32,null=True)
    publicStatsViewable = models.BooleanField(default=True)
    recordingLocation = models.CharField(max_length=256, null=True)
    streamStartTime = models.DateTimeField(null=True)
    streamEndTime = models.DateTimeField(null=True)
    streamConcurrentViewers = models.IntegerField(null=True)

    #statistics
    view_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    dislike_count= models.IntegerField(null=True)
    favorite_count= models.IntegerField(null=True)
    comment_count= models.IntegerField(null=True)

    #private fields
    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1)
    _file_path = models.CharField(max_length=512, null=True)


    class Meta:
        app_label = "Youtube"

    def __str__(self):
        if self.channel:
            if self.title:
                return "%s's video (%s)"%(self.channel,
                    self.title[:15]+"..."*(len(self.title)>15))
            else:
                return "%s's video #%s" % (self.channel,self._ident)
        else:
            return 'video #%s'%self._ident

    def get_obj_ident(self):
        return "YTVideo__%s" % self.pk

    def ident(self):
        return self._ident

    def shortTitle(self):
        if self.title:
            return self.title[:15]+'...'*(len(self.title)>15)

    def title_underscore(self):
        return re.sub(' ', '_',self.title)

    def get_fields_description(self):
        return {
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique de la vidéo'
            },
            'description': {
                'name': 'Description',
                'description': 'Description du contenu de la vidéo'
            },
            'contentRating_raw': {
                'name': 'Évaluation du contenu',
                'description': 'Évaluation publique du contenu de la vidéo'
            },
            'channel': {
                'name': 'Auteur',
                'description': 'Chaîne Youtube ayant posté la vidéo'
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre de la vidéo'
            },
            'publicStatsViewable': {
                'name': 'Statistiques publiques',
                'description': 'Determine si l''auteur partage publiquement les statistiques de la vidéo (nombre de vues, nombre de commentaires, etc.)'
            },
            'publishedAt': {
                'name': 'Date de publication',
                'description': 'Date de publication de la vidéo'
            },
            'recordingLocation': {
                'name': 'Location d''enregistrement',
                'description': 'Location à laquelle la vidéo a été créée/éditée/postée'
            },
            'streamStartTime': {
                'name': 'Temps de départ stream',
                'description': 'Si la vidéo est un livestream, temps de démarage du livestream'
            },
            'streamEndTime': {
                'name': 'Temps de fin du stream',
                'description': 'Si la vidéo est un livestream, temps de fin du livestream'
            },
            'streamConcurrentViewers': {
                'name': 'Vues concurentes du stream',
                'description': 'Si la vidéo est un livestream, nombre maximum de vues en simultané'
            },
            'comment_count': {
                'name': 'Nombre de commentaires',
                'description': 'Nombre de commentaires postés dans la section discussion (au moment de la dernière mise à jour)'
            },
            'like_count': {
                'name': 'Nombre de likes',
                'description': 'Nombre de likes de la vidéo (au moment de la dernière mise à jour)'
            },
            'dislike_count': {
                'name': 'Nombre de dislikes',
                'description': 'Nombre de dislikes de la vidéo (au moment de la dernière mise à jour)'
            },
            'favorite_count': {
                'name': 'Nombre de favoris',
                'description': 'Nombre de personnes ayant ajouté la vidéo à leurs "favoris" (au moment de la dernière mise à jour)'
            },
            'view_count': {
                'name': 'Nombre de vues',
                'description': 'Nombre de vues total de la vidéo (au moment de la dernière mise à jour)'
            },
            '_deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle la vidéo à été supprimée (si applicable)'
            },
        }

    basicFields = {
        '_ident':                   ['id'],
        'title':                    ['snippet','title'],
        'description':              ['snippet','description'],
        'contentRating_raw':        ['contentRating'],
        'privacyStatus':            ['status','privacyStatus'],
        'publicStatsViewable':      ['status','publicStatsViewable'],
        'recordingLocation':        ['recordingDetails','locationDescription'],
        'streamConcurrentViewers':  ['liveStreamingDetails', 'concurrentViewers'],
        'view_count':               ['statistics','viewCount'],
        'like_count':               ['statistics','likeCount'],
        'dislike_count':            ['statistics','dislikeCount'],
        'favorite_count':           ['statistics','favoriteCount'],
        'comment_count':            ['statistics','commentCount'],
    }
    dateTimeFields = {
        'publishedAt':              ['snippet', 'publishedAt'],
        'streamStartTime':          ['liveStreamingDetails', 'actualStartTime'],
        'streamEndTime':            ['liveStreamingDetails','actualEndTime'],
    }
    statistics = {
        'view_counts':               ['statistics', 'viewCount'],
        'like_counts':               ['statistics', 'likeCount'],
        'dislike_counts':            ['statistics', 'dislikeCount'],
        'favorite_counts':           ['statistics', 'favoriteCount'],
        'comment_counts':            ['statistics', 'commentCount'],
    }

    def update(self, jObject):
        assert isinstance(jObject, dict), 'jObject must be a dict or json instance!'
        self.copyBasicFields(jObject)
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateImages(jObject)
        self._last_updated = today()
        self.save()

    #@youtubeLogger.debug()
    def copyBasicFields(self,jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    setattr(self, attr, val)

    #@youtubeLogger.debug()
    def copyDateTimeFields(self, jObject):
        for attr in self.dateTimeFields:
            if self.dateTimeFields[attr][0] in jObject:
                val = jObject[self.dateTimeFields[attr][0]]
                for key in self.dateTimeFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
                    val = val.replace(tzinfo=utc)
                    setattr(self, attr, val)

    #@youtubeLogger.debug()
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    #log('Invalid dict sequence: %s. Object returned is: %s' % (self.statistics[attrName],val))
                    val=None
            if val:
                if not countObjs.exists():
                    objType.objects.create(video=self, value=val)
                elif countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(video=self, value=val)

    def updateImages(self,jObject):
        pass

# OBJECT SAMPLE. MORE AT https://developers.google.com/youtube/v3/docs/activities
'''
{
  "kind": "youtube#video",
  "etag": etag,
  "id": string,
  "snippet": {
    "publishedAt": datetime,
    "channelId": string,
    "title": string,
    "description": string,
    "thumbnails": {
      (key): {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
      }
    },
    "channelTitle": string,
    "tags": [
      string
    ],
    "categoryId": string,
    "liveBroadcastContent": string,
    "defaultLanguage": string,
    "localized": {
      "title": string,
      "description": string
    },
    "defaultAudioLanguage": string
  },
  "contentDetails": {
    "duration": string,
    "dimension": string,
    "definition": string,
    "caption": string,
    "licensedContent": boolean,
    "regionRestriction": {
      "allowed": [
        string
      ],
      "blocked": [
        string
      ]
    },
    "contentRating": {
      "acbRating": string,
      "agcomRating": string,
      "anatelRating": string,
      "bbfcRating": string,
      "bfvcRating": string,
      "bmukkRating": string,
      "catvRating": string,
      "catvfrRating": string,
      "cbfcRating": string,
      "cccRating": string,
      "cceRating": string,
      "chfilmRating": string,
      "chvrsRating": string,
      "cicfRating": string,
      "cnaRating": string,
      "cncRating": string,
      "csaRating": string,
      "cscfRating": string,
      "czfilmRating": string,
      "djctqRating": string,
      "djctqRatingReasons": [,
        string
      ],
      "ecbmctRating": string,
      "eefilmRating": string,
      "egfilmRating": string,
      "eirinRating": string,
      "fcbmRating": string,
      "fcoRating": string,
      "fmocRating": string,
      "fpbRating": string,
      "fskRating": string,
      "grfilmRating": string,
      "icaaRating": string,
      "ifcoRating": string,
      "ilfilmRating": string,
      "incaaRating": string,
      "kfcbRating": string,
      "kijkwijzerRating": string,
      "kmrbRating": string,
      "lsfRating": string,
      "mccaaRating": string,
      "mccypRating": string,
      "mdaRating": string,
      "medietilsynetRating": string,
      "mekuRating": string,
      "mibacRating": string,
      "mocRating": string,
      "moctwRating": string,
      "mpaaRating": string,
      "mtrcbRating": string,
      "nbcRating": string,
      "nbcplRating": string,
      "nfrcRating": string,
      "nfvcbRating": string,
      "nkclvRating": string,
      "oflcRating": string,
      "pefilmRating": string,
      "rcnofRating": string,
      "resorteviolenciaRating": string,
      "rtcRating": string,
      "rteRating": string,
      "russiaRating": string,
      "skfilmRating": string,
      "smaisRating": string,
      "smsaRating": string,
      "tvpgRating": string,
      "ytRating": string
    },
    "projection": string
  },
  "status": {
    "uploadStatus": string,
    "failureReason": string,
    "rejectionReason": string,
    "privacyStatus": string,
    "publishAt": datetime,
    "license": string,
    "embeddable": boolean,
    "publicStatsViewable": boolean
  },
  "statistics": {
    "viewCount": unsigned long,
    "likeCount": unsigned long,
    "dislikeCount": unsigned long,
    "favoriteCount": unsigned long,
    "commentCount": unsigned long
  },
  "player": {
    "embedHtml": string
  },
  "topicDetails": {
    "topicIds": [
      string
    ],
    "relevantTopicIds": [
      string
    ]
  },
  "recordingDetails": {
    "locationDescription": string,
    "location": {
      "latitude": double,
      "longitude": double,
      "altitude": double
    },
    "recordingDate": datetime
  },
  "fileDetails": {
    "fileName": string,
    "fileSize": unsigned long,
    "fileType": string,
    "container": string,
    "videoStreams": [
      {
        "widthPixels": unsigned integer,
        "heightPixels": unsigned integer,
        "frameRateFps": double,
        "aspectRatio": double,
        "codec": string,
        "bitrateBps": unsigned long,
        "rotation": string,
        "vendor": string
      }
    ],
    "audioStreams": [
      {
        "channelCount": unsigned integer,
        "codec": string,
        "bitrateBps": unsigned long,
        "vendor": string
      }
    ],
    "durationMs": unsigned long,
    "bitrateBps": unsigned long,
    "recordingLocation": {
      "latitude": double,
      "longitude": double,
      "altitude": double
    },
    "creationTime": string
  },
  "processingDetails": {
    "processingStatus": string,
    "processingProgress": {
      "partsTotal": unsigned long,
      "partsProcessed": unsigned long,
      "timeLeftMs": unsigned long
    },
    "processingFailureReason": string,
    "fileDetailsAvailability": string,
    "processingIssuesAvailability": string,
    "tagSuggestionsAvailability": string,
    "editorSuggestionsAvailability": string,
    "thumbnailsAvailability": string
  },
  "suggestions": {
    "processingErrors": [
      string
    ],
    "processingWarnings": [
      string
    ],
    "processingHints": [
      string
    ],
    "tagSuggestions": [
      {
        "tag": string,
        "categoryRestricts": [
          string
        ]
      }
    ],
    "editorSuggestions": [
      string
    ]
  },
  "liveStreamingDetails": {
    "actualStartTime": datetime,
    "actualEndTime": datetime,
    "scheduledStartTime": datetime,
    "scheduledEndTime": datetime,
    "concurrentViewers": unsigned long,
    "activeLiveChatId": string
  },
  "localizations": {
    (key): {
      "title": string,
      "description": string
    }
  }
}
'''

class CommentCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='comment_counts',null=True)
    video = models.ForeignKey(YTVideo, related_name='comment_counts', null=True)
class ViewCount(Big_integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='view_counts', null=True)
    video = models.ForeignKey(YTVideo, related_name='view_counts', null=True)
class DislikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='dislike_counts', null=True)
class FavoriteCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='favorite_counts', null=True)
class ContentImage(Image_time_label):
    channel = models.ForeignKey(YTChannel, related_name='images',null=True)
    video = models.ForeignKey(YTVideo, related_name='images', null=True)

#######################  YTPLAYLIST  #####################

class YTPlaylist(models.Model):
    channel = models.ForeignKey(YTChannel, related_name='playlists', null=True)
    _ident = models.CharField(max_length=64)
    title = models.CharField(max_length=256, null=True)
    description = models.CharField(max_length=4096, null=True)
    publishedAt = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    privacy_status = models.CharField(max_length=32, null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _last_video_harvested = models.DateTimeField(null=True)
    _error_on_harvest = models.BooleanField(default=False)


    class Meta:
        app_label = "Youtube"

    def __str__(self):
        if self.title:
            return "Playlist ('%s%s')"%(self.title[:50], "..." if len(self.title)>50 else "")
        if self.channel:
            return "%s's playlist"%self.channel

    def videos(self):
        return self.items.order_by('playlistOrder').values('video')

    def videoCount(self):
        return self.items.count()


    def get_fields_description(self):
        return {
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique de la playlist'
            },
            'channel': {
                'name': 'Chaîne',
                'description': 'Chaîne sur laquelle la playlist est présentée'
            },
            'title': {
                'name': 'Titre',
                'description': 'Titre donné à la playlist'
            },
            'description': {
                'name': 'Description',
                'description': 'Description du contenu de la playlist'
            },
            'publishedAt': {
                'name': 'Publication',
                'description': 'Date de publication de la playlist'
            },
            'deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle la playlist a été supprimée, si applicable'
            },
            'privacy_status': {
                'name': 'Status de confidentialité',
                'description': 'Niveau de confidentialité de la playlist (public, private, hidden, etc)'
            }
        }

    def get_obj_ident(self):
        return "YTPlaylist__%s" % self.pk


    def ident(self):
        return self._ident

    def update(self, jObject):
        if not self.channel:
            self.updateChannel(jObject)
        self.title          = jObject['snippet']['title']
        self.description    = jObject['snippet']['description']
        publishedAt = datetime.strptime(jObject['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        publishedAt = publishedAt.replace(tzinfo=utc)
        self.publishedAt    = publishedAt
        self.privacy_status = jObject['status']['privacyStatus']
        self._last_updated = today()
        self.save()



    def updateChannel(self, jObject):
        channel, new = YTChannel.objects.get_or_create(_ident=jObject['snippet']['channelId'])
        if new:
            channelUpdateQueue.put(channel)
        self.channel = channel


# OBJECT SAMPLE. MORE AT https://developers.google.com/youtube/v3/docs/playlists
'''
{
  "kind": "youtube#playlist",
  "etag": etag,
  "id": string,
  "snippet": {
    "publishedAt": datetime,
    "channelId": string,
    "title": string,
    "description": string,
    "thumbnails": {
      (key): {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
      }
    },
    "channelTitle": string,
    "tags": [
      string
    ],
    "defaultLanguage": string,
    "localized": {
      "title": string,
      "description": string
    }
  },
  "status": {
    "privacyStatus": string
  },
  "contentDetails": {
    "itemCount": unsigned integer
  },
  "player": {
    "embedHtml": string
  },
  "localizations": {
    (key): {
      "title": string,
      "description": string
    }
  }
}
'''


class YTPlaylistItem(models.Model):

    playlist = models.ForeignKey(YTPlaylist, related_name='items')
    video = models.ForeignKey(YTVideo, related_name='playlistsSpots')
    playlistOrder = models.IntegerField(null=True)

    def get_fields_description(self):
        fields = {
            'playlistOrder': {
                'name': 'Playlist position',
                'description': 'Position in the playlist'
            },
        }
        videoFields = YTVideo().get_fields_description()
        for key in videoFields:
            fields['video__%s'%key] = videoFields[key]
        return fields

    def get_obj_ident(self):
        return "YTPlaylistItem__%s" % self.pk

    class Meta:
        app_label = "Youtube"


#######################  YTCOMMENT  ######################

class YTComment(models.Model):
    # basic fields
    video_target = models.ForeignKey(YTVideo, related_name='comments', null=True)
    channel_target = models.ForeignKey(YTChannel, related_name='comments', null=True)
    parent_comment = models.ForeignKey("self", related_name='replies', null=True)
    author = models.ForeignKey(YTChannel, related_name='posted_comments',null=True)
    _ident = models.CharField(max_length=128)
    _text_max_length = 8192
    text =  models.CharField(max_length=_text_max_length, null=True)
    text_truncated = models.BooleanField(default=False)
    publishedAt = models.DateTimeField(null=True)
    updatedAt = models.DateTimeField(null=True)

    # statistics
    likeCount = models.BigIntegerField(default=0)
    numberOfReplies = models.IntegerField(default=0)

    # private fields
    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=2)


    def get_fields_description(self):
        return {
            'video_target': {
                'name': 'Video parente',
                'description': 'Video Youtube à laquelle le commentaire est addressé'
            },
            'channel_target': {
                'name': 'Chaîne parente',
                'description': 'Chaîne Youtube à laquelle le commentaire est addressé'
            },
            'parent_comment': {
                'name': 'Commentaire parent',
                'description': 'Commentaire auquel le commentaire est addressé'
            },
            'author': {
                'name': 'Auteur',
                'description': 'Chaîne de l''auteur du commentaire'
            },
            '_ident': {
                'name': 'Identifiant',
                'description': 'Identifiant unique du commentaire'
            },
            'text': {
                'name': 'Texte',
                'description': 'Contenu textuel du commentaire'
            },
            'text_truncated': {
                'name': 'Texte raccourci',
                'description': 'Détermine si le texte du commentaire a été racourci par Aspira pour être enregistré dans la base de données. Auquel cas il est racourci à %s caratères' % self._text_max_length
            },
            'publishedAt': {
                'name': 'Date de publication',
                'description': 'Date de publication initiale du commentaire'
            },
            'updatedAt': {
                'name': 'Date de dernière modification',
                'description': 'Date de la dernière édition du commentaire, si applicable'
            },
            'likeCount': {
                'name': 'Nombre de likes',
                'description': 'Nombre de likes que le commentaire a reçu (au moment de la dernière mise à jour)'
            },
            '_deleted_at': {
                'name': 'Date de deletion',
                'description': 'Date à laquelle le commentaire a été supprimé, si applicable'
            },
            'numberOfReplies': {
                'name': 'Nombre de réponses',
                'description': 'Nombre de commentaires répondant au commentaire, si applicable'
            },
        }


    basicFields = {
        '_ident':               ['id'],
        'text':                 ['snippet','textDisplay'],
    }
    dateTimeFields = {
        'publishedAt':          ['snippet','publishedAt'],
        'updatedAt':            ['snippet','updatedAt'],
    }
    statistics = {
        'like_counts': ['snippet', 'likeCount'],
    }

    class Meta:
        app_label = "Youtube"

    def __str__(self):
        target = self.parent_comment or self.video_target or self.channel_target or "an unidentified target"
        author = self.author or "An unidentified user"
        type = 'reply' if self.parent_comment else 'comment'
        return "%s\'s %s on %s"%(author, type, target)

    def get_obj_ident(self):
        return "YTComment__%s" % self.pk

    def ident(self):
        return self._ident

    def update(self, jObject):
        assert isinstance(jObject, dict), 'jObject must be a dict or json instance!'
        #pretty(jObject)
        self.copyBasicFields(jObject)
        self.truncate_text()
        self.copyDateTimeFields(jObject)
        self.updateStatistics(jObject)
        self.updateAuthor(jObject)
        self.updateChannelTarget(jObject)
        self.updateParentComment(jObject)
        self.updateVideoTarget(jObject)
        self._last_updated = today()
        self.save()


    def truncate_text(self):
        if not self.text:
            self.text = ""
        if len(self.text) >= self._text_max_length:
            self.text = self.text[0: self._text_max_length - 3] + '...'
            log('%s''s text has been truncated!'%self)


    # @youtubeLogger.debug()
    def copyBasicFields(self, jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    setattr(self, attr, val)

    # @youtubeLogger.debug()
    def copyDateTimeFields(self, jObject):
        for attr in self.dateTimeFields:
            if self.dateTimeFields[attr][0] in jObject:
                val = jObject[self.dateTimeFields[attr][0]]
                for key in self.dateTimeFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
                    val = val.replace(tzinfo=utc)
                    setattr(self, attr, val)

    # @youtubeLogger.debug()
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    log('Invalid dict sequence: %s' % self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(comment=self, value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(comment=self, value=val)

    def updateVideoTarget(self, jObject):
        if self.video_target: return
        if self.parent_comment: return
        if 'videoId' in jObject['snippet']:
            if self.channel_target:
                video, new = YTVideo.objects.get_or_create(_ident=jObject['snippet']['videoId'],channel=self.channel_target)
            elif YTVideo.objects.filter(_ident=jObject['snippet']['videoId']).exists():
                video = YTVideo.objects.get(_ident=jObject['snippet']['videoId'])
                self.channel_target = video.channel
                new = False
            else:
                return
            if new:
                videoToUpdateQueue.put(video)
            self.video_target = video
            #video.numberOfReplies = video.replies.count()
            #video.save()

    def updateChannelTarget(self, jObject):
        if 'channelId' in jObject['snippet']:
            channel = YTChannel.objects.get(_ident=jObject['snippet']['channelId'])
            self.channel_target = channel

    def updateAuthor(self, jObject):
        if self.author: return
        if 'authorChannelId' in jObject['snippet'] and jObject['snippet']['authorChannelId']['value'] != '':
            channel, new = YTChannel.objects.get_or_create(_ident=jObject['snippet']['authorChannelId']['value'])
            if new:
                channelUpdateQueue.put(channel)
                channelToSubsHarvestQueue.put(channel)
            self.author = channel

    def updateParentComment(self, jObject):
        if self.parent_comment: return
        if 'parentId' in jObject['snippet']:
            comment, new = YTComment.objects.get_or_create(_ident=jObject['snippet']['parentId'])
            if new:
                commentToUpdateQueue.put(comment)
            self.parent_comment = comment



# OBJECT SAMPLE. MORE AT https://developers.google.com/youtube/v3/docs/comments
'''
{
    "kind": "youtube#comment",
    "etag": etag,
    "id": string,
    "snippet": {
        "authorDisplayName": string,
        "authorProfileImageUrl": string,
        "authorChannelUrl": string,
        "authorChannelId": {
            "value": string
        },
        "channelId": string,
        "videoId": string,
        "textDisplay": string,
        "textOriginal": string,
        "parentId": string,
        "canRate": boolean,
        "viewerRating": string,
        "likeCount": unsigned integer,
        "moderationStatus": string,
        "publishedAt": datetime,
        "updatedAt": datetime
    }
}
'''


class LikeCount(Big_integer_time_label):
    video = models.ForeignKey(YTVideo, related_name='like_counts', null=True)
    comment = models.ForeignKey(YTComment, related_name='like_counts', null=True)