from django.db import models
import requests, time, re
from SocialNetworkHarvester_v1p0.models import *
from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG, FACEBOOK_APP_PARAMS

from datetime import datetime
from django.utils.timezone import utc
today = lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)

log = lambda s: facebookLogger.log(s) if DEBUG else 0
pretty = lambda s: facebookLogger.pretty(s) if DEBUG else 0


####################  ACTUAL MODELS  ##########################

class FBLocation(models.Model):
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null = True)
    longitude = models.FloatField(null = True)
    state = models.CharField(max_length=16, null=True)
    street = models.CharField(max_length=512, null=True)
    zip = models.CharField(max_length=255, null=True)

    def update(self, jObject):
        for attr in ['city','country','latitude','longitude','state','street','zip']:
            if attr in jObject:
                setattr(self, attr, jObject[attr])
        self.save()


class FBVideo(models.Model):
    _ident = models.CharField(max_length=255)
    description = models.TextField(null=True)
    updated_time = models.DateTimeField(null=True)


    def update(self, jObject):
        self._ident = jObject['id']
        self.description = jObject['description']
        updated_time = datetime.strptime(jObject['updated_time'], '%Y-%m-%dT%H:%M:%S+0000') #'2017-02-23T23:11:46+0000'
        self.updated_time = updated_time.replace(tzinfo=utc)
        self.save()


class FBUser(models.Model):
    _ident = models.CharField(max_length=225)
    name = models.CharField(max_length=256, null=True)

    def get_obj_ident(self):
        return "FBUser__%s"%self.pk

    def get_fields_description(self):
        return {"_ident": {
            "_ident": "Identifiant numérique de la personne",
            "name": "Identifiant"},
            "name": {
                "description": "Le nom affiché de la personne",
                "name": "Nom"},
        }


class FBPage(models.Model):
    _ident = models.CharField(max_length=225)
    category = models.CharField(max_length=128)

    ### Core fields ###
    name = models.CharField(max_length=128, null=True)
    username = models.CharField(max_length=64, null=True)
    about = models.TextField(null=True)
    cover = models.CharField(max_length=512, null=True)
    current_location = models.CharField(max_length=512, null=True)
    description_html = models.TextField(null=True)
    #display_subtext = models.CharField(max_length=1024, null=True) useless, redundant information
    #displayed_message_response_time = models.CharField(max_length=128, null=True) useless
    emails = models.CharField(max_length=2048, null=True)
    featured_video = models.ForeignKey(FBVideo,null=True, related_name='featured_on_pages')
    general_info = models.TextField( null=True)
    #impressum = models.CharField(max_length=128, null=True)
    link = models.CharField(max_length=128, null=True)
    members = models.TextField(null=True)
    is_community_page = models.BooleanField(default=False)
    is_unclaimed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    location = models.ForeignKey(FBLocation, null=True)
    parent_page = models.ForeignKey('self', null=True)
    phone = models.CharField(max_length=256, null=True)
    verification_status = models.CharField(max_length=64, null=True)
    website = models.CharField(max_length=256, null=True)

    ### Statistics fields ###
    checkins = models.IntegerField(null=True)
    fan_count = models.IntegerField(null=True)
    overall_star_rating = models.FloatField(null=True)
    rating_count = models.IntegerField(null=True)
    talking_about_count = models.IntegerField(null=True)
    were_here_count = models.IntegerField(null=True)

    ### People ###
    birthday = models.CharField(max_length=128, null=True)
    affiliation = models.CharField(max_length=225, null=True)
    personal_info = models.TextField(null=True)
    personal_interests = models.TextField(null=True)

    ### Vehicules ###
    built = models.CharField(max_length=4, null=True)
    features = models.TextField(null=True)
    mpg = models.CharField(max_length=64, null=True) # mpg = miles per gallons... yep.

    ### Compagnies, restaurants, nightlife ###
    company_overview = models.TextField(null=True)
    mission = models.TextField(null=True)
    products = models.TextField(null=True)
    founded = models.TextField(null=True)
    general_manager = models.CharField(max_length=256, null=True)
    price_range = models.CharField(max_length=16, null=True) # can be $, $$, $$$, $$$$ or Unspecified
    hours = models.TextField(null=True)
    pharma_safety_info = models.TextField(null=True)
    is_permanently_closed = models.BooleanField(default=False)
    is_always_open = models.BooleanField(default=False)

    ### TV Shows and films ###
    network = models.CharField(max_length=128,null=True)
    schedule = models.TextField(null=True)
    season = models.CharField(max_length=64,null=True)
    written_by = models.CharField(max_length=512,null=True)
    awards = models.TextField(null=True)
    directed_by = models.TextField(null=True)
    genre = models.TextField(null=True)
    plot_outline = models.TextField(null=True)
    produced_by = models.TextField(null=True)
    release_date = models.CharField(max_length=64,null=True)
    screenplay_by = models.TextField(null=True)
    starring = models.TextField(null=True)
    studio = models.TextField(null=True)

    ### Musicians and bands ###
    artists_we_like = models.TextField(null=True)
    band_interests = models.TextField(null=True)
    band_members = models.CharField(max_length=2048,null=True)
    bio = models.TextField(null=True)
    booking_agent = models.TextField(null=True)
    hometown = models.TextField(null=True)
    influences = models.TextField(null=True)
    press_contact = models.TextField(null=True)
    record_label = models.TextField(null=True)

    ### Functionnal private fields ###
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)
    last_feed_harvested = models.DateTimeField(null=True)

    def __str__(self):
        return "%s's Facebook Page"%self.name

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "_ident",
                "description": ""
            },
            "category": {
                "name": "category",
                "description": ""
            },
            "name": {
                "name": "name",
                "description": ""
            },
            "username": {
                "name": "username",
                "description": ""
            },
            "about": {
                "name": "about",
                "description": ""
            },
            "cover": {
                "name": "cover",
                "description": ""
            },
            "current_location": {
                "name": "current_location",
                "description": ""
            },
            "description_html": {
                "name": "description_html",
                "description": ""
            },
            "emails": {
                "name": "emails",
                "description": ""
            },
            "featured_video": {
                "name": "featured_video",
                "description": ""
            },
            "general_info": {
                "name": "general_info",
                "description": ""
            },
            "link": {
                "name": "link",
                "description": ""
            },
            "members": {
                "name": "members",
                "description": ""
            },
            "is_community_page": {
                "name": "is_community_page",
                "description": ""
            },
            "is_unclaimed": {
                "name": "is_unclaimed",
                "description": ""
            },
            "is_verified": {
                "name": "is_verified",
                "description": ""
            },
            "location": {
                "name": "location",
                "description": ""
            },
            "parent_page": {
                "name": "parent_page",
                "description": ""
            },
            "phone": {
                "name": "phone",
                "description": ""
            },
            "verification_status": {
                "name": "verification_status",
                "description": ""
            },
            "website": {
                "name": "website",
                "description": ""
            },
            "checkins": {
                "name": "checkins",
                "description": ""
            },
            "fan_count": {
                "name": "fan_count",
                "description": ""
            },
            "overall_star_rating": {
                "name": "overall_star_rating",
                "description": ""
            },
            "rating_count": {
                "name": "rating_count",
                "description": ""
            },
            "talking_about_count": {
                "name": "talking_about_count",
                "description": ""
            },
            "were_here_count": {
                "name": "were_here_count",
                "description": ""
            },
            "birthday": {
                "name": "birthday",
                "description": ""
            },
            "affiliation": {
                "name": "affiliation",
                "description": ""
            },
            "personal_info": {
                "name": "personal_info",
                "description": ""
            },
            "personal_interests": {
                "name": "personal_interests",
                "description": ""
            },
            "built": {
                "name": "built",
                "description": ""
            },
            "features": {
                "name": "features",
                "description": ""
            },
            "mpg": {
                "name": "mpg",
                "description": ""
            },
            "company_overview": {
                "name": "company_overview",
                "description": ""
            },
            "mission": {
                "name": "mission",
                "description": ""
            },
            "products": {
                "name": "products",
                "description": ""
            },
            "founded": {
                "name": "founded",
                "description": ""
            },
            "general_manager": {
                "name": "general_manager",
                "description": ""
            },
            "price_range": {
                "name": "price_range",
                "description": ""
            },
            "hours": {
                "name": "hours",
                "description": ""
            },
            "pharma_safety_info": {
                "name": "pharma_safety_info",
                "description": ""
            },
            "is_permanently_closed": {
                "name": "is_permanently_closed",
                "description": ""
            },
            "is_always_open": {
                "name": "is_always_open",
                "description": ""
            },
            "network": {
                "name": "network",
                "description": ""
            },
            "schedule": {
                "name": "schedule",
                "description": ""
            },
            "season": {
                "name": "season",
                "description": ""
            },
            "written_by": {
                "name": "written_by",
                "description": ""
            },
            "awards": {
                "name": "awards",
                "description": ""
            },
            "directed_by": {
                "name": "directed_by",
                "description": ""
            },
            "genre": {
                "name": "genre",
                "description": ""
            },
            "plot_outline": {
                "name": "plot_outline",
                "description": ""
            },
            "produced_by": {
                "name": "produced_by",
                "description": ""
            },
            "release_date": {
                "name": "release_date",
                "description": ""
            },
            "screenplay_by": {
                "name": "screenplay_by",
                "description": ""
            },
            "starring": {
                "name": "starring",
                "description": ""
            },
            "studio": {
                "name": "studio",
                "description": ""
            },
            "artists_we_like": {
                "name": "artists_we_like",
                "description": ""
            },
            "band_interests": {
                "name": "band_interests",
                "description": ""
            },
            "band_members": {
                "name": "band_members",
                "description": ""
            },
            "bio": {
                "name": "bio",
                "description": ""
            },
            "booking_agent": {
                "name": "booking_agent",
                "description": ""
            },
            "hometown": {
                "name": "hometown",
                "description": ""
            },
            "influences": {
                "name": "influences",
                "description": ""
            },
            "press_contact": {
                "name": "press_contact",
                "description": ""
            },
            "record_label": {
                "name": "record_label",
                "description": ""
            },
        }

    def get_obj_ident(self):
        return "FBPage__%s"%self.pk

    def getProfile(self):
        if not hasattr(self,'fbProfile'):
            FBProfile.objects.create(_ident=self._ident,type="P",fbPage=self)
        return self.fbProfile


    ### UPDATE ROUTINE METHODS ###
    basicFields = {
        '_ident': ['id'],
        'category': ['category'],
        'checkins': ['checkins'],
        'fan_count': ['fan_count'],
        'overall_star_rating': ['overall_star_rating'],
        'rating_count': ['rating_count'],
        'talking_about_count': ['talking_about_count'],
        'were_here_count': ['were_here_count'],
        'name':['name'],
        'username':['username'],
        'about':['about'],
        'cover':['cover','source'],
        'current_location':['current_location'],
        'description_html':['description_html'],
        'emails':['emails'],
        'general_info':['general_info'],
        'link':['link'],
        'members':['members'],
        'is_community_page':['is_community_page'],
        'is_unclaimed':['is_unclaimed'],
        'is_verified':['is_verified'],
        'phone':['phone'],
        'verification_status':['verification_status'],
        'website':['website'],
        'birthday':['birthday'],
        'affiliation':['affiliation'],
        'personal_info':['personal_info'],
        'personal_interests':['personal_interests'],
        'built':['built'],
        'features':['features'],
        'mpg':['mpg'],
        'company_overview':['company_overview'],
        'mission':['mission'],
        'products':['products'],
        'founded':['founded'],
        'general_manager':['general_manager'],
        'price_range':['price_range'],
        'hours':['hours'],
        'pharma_safety_info':['pharma_safety_info'],
        'is_permanently_closed':['is_permanently_closed'],
        'is_always_open':['is_always_open'],
        'network':['network'],
        'schedule':['schedule'],
        'season':['season'],
        'written_by':['written_by'],
        'awards':['awards'],
        'directed_by':['directed_by'],
        'genre':['genre'],
        'plot_outline':['plot_outline'],
        'produced_by':['produced_by'],
        'screenplay_by':['screenplay_by'],
        'starring':['starring'],
        'studio':['studio'],
        'artists_we_like':['artists_we_like'],
        'band_interests':['band_interests'],
        'band_members':['band_members'],
        'bio':['bio'],
        'booking_agent':['booking_agent'],
        'hometown':['hometown'],
        'influences':['influences'],
        'press_contact':['press_contact'],
        'record_label':['record_label'],
    }

    statistics = {
        'checkins_counts':['checkins'],
        'fan_counts':['fan_count'],
        'overall_star_rating_counts':['overall_star_rating'],
        'rating_counts':['rating_count'],
        'talking_about_counts':['talking_about_count'],
        'were_here_counts':['were_here_count'],
    }

    @facebookLogger.debug(showClass=True)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')

        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        self.updateFeaturedVideo(jObject)
        self.setParentPage(jObject)
        self.setLocation(jObject)
        self.setReleaseDate(jObject)
        self.last_updated = today()
        self.save()

    # @youtubeLogger.debug(showArgs=True)
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
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    pass
                    # log('Invalid dict sequence: %s'%self.statistics[attrName])
            if not countObjs.exists():
                objType.objects.create(fbPage=self, value=val)
            else:
                if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                    objType.objects.create(fbPage=self, value=val)

    def updateFeaturedVideo(self,jObject):
        if "featured_video" in jObject:
            video, new = FBVideo.objects.get_or_create(_ident=jObject['featured_video']['id'])
            video.update(jObject['featured_video'])
            self.featured_video = video

    def setParentPage(self, jObject):
        if 'parent_page' in jObject:
            log('PARENT PAGE: %s'%jObject['parent_page'])
            #page, new = FBPage.objects.get_or_create(_ident=jObject['parent_page']['id'])
            #page.update()

    def setLocation(self, jObject):
        if 'location' in jObject:
            location = self.location
            if not location:
                location = FBLocation.objects.create()
                self.location = location
            location.update(jObject['location'])

    def setReleaseDate(self,jObject):
        if 'release_date' in jObject:
            release_date = datetime.strptime(jObject['release_date'],'%Y%m%d')
            self.release_date = release_date.replace(tzinfo=utc)

class checkins_count(Integer_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="checkins_counts")
class fan_count(Integer_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="fan_counts")
class overall_star_rating_count(Float_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="overall_star_rating_counts")
class rating_count(Integer_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="rating_counts")
class talking_about_count(Integer_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="talking_about_counts")
class were_here_count(Integer_time_label):
    fbPage = models.ForeignKey(FBPage, related_name="were_here_counts")



class FBGroup(models.Model):
    _ident = models.CharField(max_length=256)

class FBEvent(models.Model):
    _ident = models.CharField(max_length=256)

class FBApplication(models.Model):
    _ident = models.CharField(max_length=256)


class FBProfile(models.Model):
    '''
    A Facebook "Profile" object can be any one of the following:
    <FBUser>, <FBPage>, <FBGroup>, <FBEvent>, <FBApplication>.
    FBProfile is used here to simplify the database structure.
    '''
    _ident = models.CharField(max_length=225)
    type = models.CharField(max_length=1)  # U/P/G/E/A

    ### A single one of the following fields is non-null ###
    fbUser = models.OneToOneField(FBUser, null=True, related_name='fbProfile')
    fbPage = models.OneToOneField(FBPage, null=True, related_name='fbProfile')
    fbGroup = models.OneToOneField(FBGroup, null=True, related_name='fbProfile')
    fbEvent = models.OneToOneField(FBEvent, null=True, related_name='fbProfile')
    fbApplication = models.OneToOneField(FBApplication, null=True, related_name='fbProfile')

    def getObj(self):
        d = {
            "U": self.fbUser,
            "P": self.fbPage,
            "G": self.fbGroup,
            "E": self.fbEvent,
            "A": self.fbApplication,
        }
        return d[self.type] if self.type in d else None


class FBPost(models.Model):
    _ident = models.CharField(max_length=255, unique=True)
    admin_creator = models.CharField(max_length=128, null=True)
    caption = models.CharField(max_length=512, null=True)
    created_time = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    from_profile = models.ForeignKey(FBProfile, related_name="postedStatuses", null=True)
    to_profiles = models.ManyToManyField(FBProfile, related_name="targetedByStatuses")
    is_hidden = models.BooleanField(default=False)
    is_instagram_eligible = models.BooleanField(default=False)
    link = models.CharField(max_length=1024, null=True)
    message = models.TextField(null=True)
    message_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostMessages")
    story = models.CharField(max_length=512, null=True)
    story_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostStories")
    name = models.CharField(max_length=256, null=True)
    object_id = models.CharField(max_length=128, null=True)
    parent_post = models.ForeignKey("self",related_name="child_posts",null=True)
    permalink_url = models.CharField(max_length=256, null=True)
    picture = models.CharField(max_length=1024, null=True)
    source = models.CharField(max_length=1024, null=True)
    status_type = models.CharField(max_length=64, null=True,)
    type = models.CharField(max_length=64, null=True, )
    updated_time = models.DateTimeField(null=True)

    ### Statistics fields ###
    share_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    comment_count = models.IntegerField(null=True)

    ### Functionnal private fields ###
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)
    last_comments_harvested = models.DateTimeField(null=True)

    def __str__(self):
        return "%s's Facebook Post" % self.ffrom.name


    def get_fields_description(self):
        return {
            "_ident": {
                "name": "_ident",
                "description": ""
            },
            "admin_creator": {
                "name": "admin_creator",
                "description": ""
            },
            "caption": {
                "name": "caption",
                "description": ""
            },
            "created_time": {
                "name": "created_time",
                "description": ""
            },
            "description": {
                "name": "description",
                "description": ""
            },
            "from_profile": {
                "name": "from_profile",
                "description": ""
            },
            "to_profile": {
                "name": "to_profile",
                "description": ""
            },
            "is_hidden": {
                "name": "is_hidden",
                "description": ""
            },
            "is_instagram_eligible": {
                "name": "is_instagram_eligible",
                "description": ""
            },
            "link": {
                "name": "link",
                "description": ""
            },
            "message": {
                "name": "message",
                "description": ""
            },
            "message_tags": {
                "name": "message_tags",
                "description": ""
            },
            "story": {
                "name": "story",
                "description": ""
            },
            "story_tags": {
                "name": "story_tags",
                "description": ""
            },
            "name": {
                "name": "name",
                "description": ""
            },
            "object_id": {
                "name": "object_id",
                "description": ""
            },
            "parent_post": {
                "name": "parent_post",
                "description": ""
            },
            "permalink_url": {
                "name": "permalink_url",
                "description": ""
            },
            "picture": {
                "name": "picture",
                "description": ""
            },
            "source": {
                "name": "source",
                "description": ""
            },
            "status_type": {
                "name": "status_type",
                "description": ""
            },
            "type": {
                "name": "type",
                "description": ""
            },
            "updated_time": {
                "name": "updated_time",
                "description": ""
            },
            "shares": {
                "name": "shares",
                "description": ""
            },
            "like_count": {
                "name": "like_count",
                "description": ""
            },
        }


    def get_obj_ident(self):
        return "FBPost__%s" % self.pk



        ### UPDATE ROUTINE METHODS ###

    basicFields = {
        'caption':              ['caption'],
        'created_time':         ['created_time'],
        'description':          ['description'],
        #'from_profile':         ['from'],
        #'to_profile':           ['to'],
        'is_hidden':            ['is_hidden'],
        'is_instagram_eligible':['is_instagram_eligible'],
        'link':                 ['link'],
        'message':              ['message'],
        #'message_tags':         ['message_tags'], #TODO: set all the connections
        'story':                ['story'],
        #'story_tags':           ['story_tags'], #TODO: set all the connections
        'name':                 ['name'],
        'object_id':            ['object_id'],
        #'parent_post':          ['parent_id'],
        'permalink_url':        ['permalink_url'],
        'picture':              ['picture'],
        'source':               ['source'],
        'status_type':          ['status_type'],
        'type':                 ['type'],
        'updated_time':         ['updated_time'],
        'share_count':          ['shares','count'],
        'like_count':           ['likes', 'summary', 'total_count'],
        'comment_count':        ['comments', 'summary', 'total_count'],
    }

    statistics = {
        'share_counts':     ['shares','count'],
        'like_counts':      ['likes','summary','total_count'],
        'comment_counts':   ['comments', 'summary', 'total_count'],
    }

    #@facebookLogger.debug(showClass=True,showArgs=True)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')

        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        self.removeEmojisFromFields(['message', 'description'])
        self.last_updated = today()
        self.save()

    # @youtubeLogger.debug(showArgs=True)
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
    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    #log('Invalid dict searching sequence: %s' % self.statistics[attrName])
                    val = None
                    break
            if val:
                if not countObjs.exists():
                    objType.objects.create(fbPost=self, value=val)
                else:
                    if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                        objType.objects.create(fbPost=self, value=val)


    def removeEmojisFromFields(self, fieldList, replacement=''):
        antiEmojiRegex = re.compile(u'['
                                    u'\U0001F300-\U0001F64F'
                                    u'\U0001F680-\U0001F6FF'
                                    u'\u2600-\u26FF\u2700-\u27BF]+',
                                    re.UNICODE)
        for field in fieldList:
            badStr = getattr(self, field)
            if badStr:
                newStr =  antiEmojiRegex.sub(badStr, replacement)
                setattr(self, field, newStr)




class share_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="share_counts")
class like_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="like_counts")
class comment_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="comment_counts")


class FBComment(models.Model):
    _ident = models.CharField(max_length=256)
    attachment = models.CharField(max_length=1024, null=True)
    created_time = models.DateTimeField(null=True)
    from_profile = models.ForeignKey(FBProfile,related_name="posted_comments")
    message = models.TextField(null=True)
    message_tags = models.CharField(max_length=1024, null=True)
    object = models.CharField(max_length=1024,null=True)
    parent = models.ForeignKey("self",related_name="fbReplies")

    ### Statistics fields ###
    comment_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)


class FBReaction(models.Model):
    from_profile = models.ForeignKey(FBProfile, related_name="reacted_to")
    to_post = models.ForeignKey(FBPost, related_name="reactions",null=True)
    to_comment = models.ForeignKey(FBComment, related_name="likes", null=True)
    type = models.CharField(max_length=10, default="LIKE")
    from_time = models.DateTimeField(default=djangoNow)
    until_time = models.DateTimeField(null=True)
