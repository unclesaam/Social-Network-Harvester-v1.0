from django.db import models
import requests, time, re
from SocialNetworkHarvester_v1p0.models import *
from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG, FACEBOOK_APP_PARAMS

from datetime import datetime
from django.utils.timezone import utc
today = lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)

log = lambda s: facebookLogger.log(s) if DEBUG else 0
pretty = lambda s: facebookLogger.pretty(s) if DEBUG else 0


####################  MODELS  ##########################

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
    _ident = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    updated_time = models.DateTimeField(null=True)


    def update(self, jObject):
        self._ident = jObject['id']
        if "description" in jObject:
            self.description = jObject['description']
        updated_time = datetime.strptime(jObject['updated_time'], '%Y-%m-%dT%H:%M:%S+0000') #'2017-02-23T23:11:46+0000'
        removeEmojisFromFields(self, ['description'])
        self.updated_time = updated_time.replace(tzinfo=utc)
        self.save()


class FBUser(models.Model):
    _ident = models.CharField(max_length=225, unique=True)
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
    def __str__(self):
        return self.name if self.name else "Utilisateur non-identifié"



class FBPage(models.Model):
    _ident = models.CharField(max_length=225,unique=True)
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
    built = models.CharField(max_length=64, null=True)
    features = models.TextField(null=True)
    mpg = models.CharField(max_length=256, null=True) # mpg = miles per gallons... yep.

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
    network = models.CharField(max_length=512,null=True)
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
        return "Page Facebook de %s"%self.name

    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
                "description": "String unique identifiant la page.",
                "type":"integer",
                "rules":['no_show']
            },
            "category": {
                "name": "Catégorie",
                "description": "Catégorie dans laquelle se retrouve la page.",
                "type":"short_string",
            },
            "name": {
                "name": "Nom",
                "description": "Nom ou titre donné à la page.",
                "type":"short_string",
            },
            "username": {
                "name": "Nom d'utilisateur",
                "description": "Nom d'authentification de la page",
                "type":"long_string",
            },
            "about": {
                "name": "À propos",
                "description": "Description de la page",
                "type":"long_string",
            },
            "cover": {
                "name": "Couverture",
                "description": "Url de l'image de couverture de la page"
            },
            "current_location": {
                "name": "Position actuelle",
                "description": "Position actuelle, si la page divulgue sa position en temps réel."
            },
            "description_html": {
                "name": "Description (html)",
                "description": "Description de la page, incluant les tags html",
                "type":"long_string",
            },
            "emails": {
                "name": "Courriels",
                "description": "Adresses courrielles associées à la page",
                "type":"long_string",
            },
            "featured_video": {
                "name": "Vidéo en vedette",
                "description": "Vidéo présentement mise en vedette par la page"
            },
            "general_info": {
                "name": "Informations générales",
                "description": "Informations générales de la page.",
                "type":"long_string",
            },
            "link": {
                "name": "Lien",
                "description": "Lien permanent vers la Page."
            },
            "members": {
                "name": "Membres",
                "description": "Personnes (profils Facebook) associés à la page, s'il s'agit d'un regroupement."
            },
            "is_community_page": {
                "name": "Est une communauté",
                "description": "(booléen) Indique s'il s'agit d'une page représentant une communauté.",
                "type":"boolean",
            },
            "is_unclaimed": {
                "name": "N'est pas réclamée",
                "description": "(Booléen) Indique si la page n'est pas réclamée par l'organisation qu'elle prétend représenter.",
                "type":"boolean",
            },
            "is_verified": {
                "name": "Vérifié",
                "description": "(Booléen) Détermine si l'identité de la page est vérifiée par la communauté Facebook",
                "type":"boolean",
            },
            "location": {
                "name": "Location",
                "description": "Position enregistrée de la page, s'il s'agit d'un commerce, etc."
            },
            "parent_page": {
                "name": "Page parente",
                "description": "Page à laquelle la page est affiliée (Page de produit affiliée à une page de compagnie, par exemple)."
            },
            "phone": {
                "name": "Téléphone",
                "description": "Numéro de téléphone."
            },
            "verification_status": {
                "name": "Status de vérification",
                "description": "État de la procédure de vérification de la page."
            },
            "website": {
                "name": "Site web",
                "description": "Lien vers le site-web du propriétaire de la page."
            },
            "checkins": {
                "name": "Entrées",
                "description": "Nombre de personnes ayant précisé qu'il étaient présent à la location de la page. (Pertinent s'il s'agit d'un pub/bar/restaurant/etc.)",
                "type": "integer",
            },
            "fan_count": {
                "name": "Fans",
                "description": "Nombre de personnes ayant aimé la page.",
                "type": "integer",
            },
            "overall_star_rating": {
                "name": "Classement",
                "description": "Classement (1 à 5 étoiles) de l'établissement.",
                "type":"integer"
            },
            "rating_count": {
                "name": "Nombre Classements",
                "description": "Nombre de notes ayant contribués au classement.",
                "type":"integer"
            },
            "talking_about_count": {
                "name": "Nombre de mentions",
                "description": "Nombre de status/commentaires mentionnant la page.",
                "type":"integer"
            },
            "were_here_count": {
                "name": "Personnes présentes",
                "description": "Nombre de personnes ayant mentionné avoir visité la location de la page",
                "type":"integer"
            },
            "birthday": {
                "name": "Anniversaire",
                "description": "Date d'aniversaire de la page, s'il s'agit d'une personne."
            },
            "affiliation": {
                "name": "Affiliation",
                "description": "Affiliation de la page, s'il s'agit d'une personalité politique"
            },
            "personal_info": {
                "name": "Infos personnelles",
                "description": "Informations personnelles de la personne, si la page représente une personne."
            },
            "personal_interests": {
                "name": "Intérêts personnels",
                "description": "Sujets d'intérêts de la pesonne."
            },
            "built": {
                "name": "Construction",
                "description": "Date de mise en ligne de la page"
            },
            "features": {
                "name": "En vedette",
                "description": "Pages mises en vedette par la page"
            },
            "mpg": {
                "name": "Miles par gallons",
                "description": "Nombre de miles pouvant être parcouru avec un gallon d'essence, si la page représente une voiture.",
                "type": "integer",
            },
            "company_overview": {
                "name": "Apperçu de compagnie",
                "description": "Apperçu général de la compagnie, si la page représente une compagnie"
            },
            "mission": {
                "name": "Mission",
                "description": "Mission ou engagement social de la compagnie."
            },
            "products": {
                "name": "Produits",
                "description": "Produits offerts par la compagnie"
            },
            "founded": {
                "name": "Fondé en",
                "description": "Date de fondation de la compagnie."
            },
            "general_manager": {
                "name": "Gérant général",
                "description": "Nom de la personne gérant la compagnie visée."
            },
            "price_range": {
                "name": "Gamme de prix",
                "description": "Gamme de prix dans laquelle l'établissement (ou le produit) se situe. Peut être $, $$, $$$ ou $$$$"
            },
            "hours": {
                "name": "Heures",
                "description": "Heures d'ouverture ou de service de l'établissement."
            },
            "pharma_safety_info": {
                "name": "Sécurité pharmaceutique",
                "description": "Informations de sécurité quand au produit, s'il s'agit d'un produit pharmaceutique."
            },
            "is_permanently_closed": {
                "name": "Permanement fermé",
                "description": "(Booléen) Indique si l'établissement est fermé de façon permanente.",
                "type":"boolean",
            },
            "is_always_open": {
                "name": "Toujours ouvert",
                "description": "(Booléen) Indique si l'établissement est ouvert à tout moment.",
                "type":"boolean",
            },
            "network": {
                "name": "Réseau",
                "description": "Réseau de diffusion ou compagnie de distribution, s'il s'agit d'un artiste ou d'un programme télévisé."
            },
            "schedule": {
                "name": "Horaire",
                "description": "Heures de diffusion de la série télévisée, si applicable."
            },
            "season": {
                "name": "Saison",
                "description": "Numéro de la saison de la série télévisé, si applicable."
            },
            "written_by": {
                "name": "Écrit par",
                "description": "Auteur de la série télévisée, si applicable."
            },
            "awards": {
                "name": "Prix gagnés",
                "description": "Prix gagnés par le film, si applicable."
            },
            "directed_by": {
                "name": "Directeur",
                "description": "Directeur ou directeurs du film, si applicable."
            },
            "genre": {
                "name": "Genre",
                "description": "Genre applicable au film, si applicable."
            },
            "plot_outline": {
                "name": "Synopsis",
                "description": "Synopsis du film, si applicable."
            },
            "produced_by": {
                "name": "Producteurs",
                "description": "Producteurs du film, si applicable."
            },
            "release_date": {
                "name": "Date de sortie",
                "description": "Date de sortie du film, si applicable."
            },
            "screenplay_by": {
                "name": "Scénarisé par",
                "description": "Scénarisateur du film, si applicable."
            },
            "starring": {
                "name": "En vedette",
                "description": "Acteurs mis en vedette dans le film, si applicable."
            },
            "studio": {
                "name": "Studio",
                "description": "Studio du film, si applicable."
            },
            "artists_we_like": {
                "name": "Artistes aimés",
                "description": "Artistes aimés par le groupe de musique, si applicable"
            },
            "band_interests": {
                "name": "Intérêts du groupe",
                "description": "Intérêts du groupe de musique, si applicable."
            },
            "band_members": {
                "name": "Membre du groupe",
                "description": "Membres du groupe de musique, si applicable."
            },
            "bio": {
                "name": "Biographie",
                "description": "Biographie du groupe de musique, si applicable."
            },
            "booking_agent": {
                "name": "Agent de réservation",
                "description": "Agent du groupe, si applicable."
            },
            "hometown": {
                "name": "Ville d'origine",
                "description": "Ville d'origine du groupe de musique, si applicable."
            },
            "influences": {
                "name": "Influences",
                "description": "Influences musicales du groupe de musique, si applicable."
            },
            "press_contact": {
                "name": "Contact de presse",
                "description": "Agent de presse du groupe de musique, si applicable."
            },
            "record_label": {
                "name": "Maison de disque",
                "description": "Maison de disque du groupe de musique, si applicable."
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

    #@facebookLogger.debug(showClass=True)
    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object from Youtube must be passed as argument.')
        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        self.updateFeaturedVideo(jObject)
        self.setParentPage(jObject)
        self.setLocation(jObject)
        self.setReleaseDate(jObject)
        removeEmojisFromFields(self, [])
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
                    val = None
                    break
            if val:
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
            try:
                release_date = datetime.strptime(jObject['release_date'],'%Y%m%d')
                self.release_date = release_date.replace(tzinfo=utc)
            except ValueError as e:
                pass # release date is in a weird format (00-indexed days of month?) TODO: filter bad dates


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
    _ident = models.CharField(max_length=255, unique=True)
class FBEvent(models.Model):
    _ident = models.CharField(max_length=255, unique=True)
class FBApplication(models.Model):
    _ident = models.CharField(max_length=255, unique=True)
class FBProfile(models.Model):
    '''
    A Facebook "Profile" object can be any one of the following:
    <FBUser>, <FBPage>, <FBGroup>, <FBEvent>, <FBApplication>.
    FBProfile is used here to simplify the database structure.
    '''
    _ident = models.CharField(max_length=225, unique=True)
    type = models.CharField(max_length=1)  # U/P/G/E/A/V
    deleted_at = models.DateTimeField(null=True)

    ### A single one of the following fields is non-null ###
    fbUser = models.OneToOneField(FBUser, null=True, related_name='fbProfile')
    fbPage = models.OneToOneField(FBPage, null=True, related_name='fbProfile')
    fbGroup = models.OneToOneField(FBGroup, null=True, related_name='fbProfile')
    fbEvent = models.OneToOneField(FBEvent, null=True, related_name='fbProfile')
    fbApplication = models.OneToOneField(FBApplication, null=True, related_name='fbProfile')

    def __str__(self):
        if self.type:
            return str(self.getInstance())
        else:
            return "Profil non-identifié"
    def getStr(self):
        return str(self)

    def findAndSetInstance(self):
        attrs = {"fbUser":FBUser, "fbPage":FBPage, "fbGroup":FBGroup, "fbEvent":FBEvent,
                 "fbApplication":FBApplication}
        for attr, model in attrs.items():
            instance = model.objects.filter(_ident=self._ident)
            if instance:
                setattr(self, attr, instance[0])
                self.save()
                return True
        return False

    def migrateId(self, newId):
        newProfile = FBProfile.objects.filter(_ident=newId).first()
        if newProfile:
            newInstance = newProfile.getInstance()
            if newInstance:
                log('migrating:')
                log('   self: %s'%self)
                log('   newInstance: %s'%newInstance)
                self.getInstance().mergeObj(newInstance) # TODO: transfer all connections to the new instance
        else:
            instance = self.getInstance()
            if instance:
                instance._ident = newId
                instance.save()
            self._ident = newId
            self.save()


    def getInstance(self):
        d = {
            "U": self.fbUser,
            "P": self.fbPage,
            "G": self.fbGroup,
            "E": self.fbEvent,
            "A": self.fbApplication,
        }
        return d[self.type] if self.type in d else None

    def update(self, jObject):
        try:
            self.setInstance(jObject['metadata']['type'])
            self.save()
        except:
            pretty(jObject)
            raise

    def setInstance(self, strType):
        if self.getInstance(): return # Object instance already set
        d = {
            "user": ("fbUser", "U", FBUser),
            "page": ("fbPage", "P", FBPage),
            "group": ("fbGroup", "G", FBGroup),
            "event": ("fbEvent", "E", FBEvent),
            "application": ("fbApplication", "A", FBApplication),
        }
        if strType  not in d.keys():
            log('profile type "%s" is not recognised'% strType)
            return
        attr, type, model = d[strType]
        setattr(self, attr, model.objects.create(_ident=self._ident))
        self.type = type

    def getLink(self):
        d = {
            "U": 'user',
            "P": 'page',
            "G": 'group',
            "E": 'event',
            "A": 'application',
        }
        if not self.type in d or not self.getInstance(): return None
        return "/facebook/%s/%s"%(d[self.type],self.getInstance().pk)


class FBPost(models.Model):
    _ident = models.CharField(max_length=255, unique=True)
    admin_creator = models.CharField(max_length=128, null=True)
    caption = models.CharField(max_length=1024, null=True)
    created_time = models.DateTimeField(null=True)
    deleted_time = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    from_profile = models.ForeignKey(FBProfile, related_name="postedStatuses", null=True)
    to_profiles = models.ManyToManyField(FBProfile, related_name="targetedByStatuses")
    is_hidden = models.BooleanField(default=False)
    is_instagram_eligible = models.BooleanField(default=False)
    link = models.CharField(max_length=1024, null=True)
    message = models.TextField(null=True)
    message_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostMessages")
    story = models.CharField(max_length=512, null=True)
    #story_tags = models.ManyToManyField(FBProfile, related_name="taggedInPostStories")
    name = models.CharField(max_length=256, null=True)
    object_id = models.CharField(max_length=128, null=True)
    parent_post = models.ForeignKey("self",related_name="child_posts",null=True)
    permalink_url = models.CharField(max_length=256, null=True)
    picture = models.CharField(max_length=2048, null=True)
    source = models.CharField(max_length=1024, null=True)
    status_type = models.CharField(max_length=64, null=True,)
    type = models.CharField(max_length=64, null=True, )
    updated_time = models.DateTimeField(null=True)

    ### Statistics fields ###
    share_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    comment_count = models.IntegerField(null=True)

    ### Management fields ###
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)
    last_comments_harvested = models.DateTimeField(null=True)
    last_reaction_harvested = models.DateTimeField(null=True)

    def __str__(self):
        from_profile = self.from_profile
        if from_profile:
            return "Status de %s" % from_profile.getInstance()
        else:
            return "Status à autheur non-identifié"
    def getStr(self):
        return str(self)

    def getTypeFrench(self):
        d = {
            'link':'Lien',
            'status':'Status',
            'photo':'Photo',
            'video':'Vidéo',
            'offer':'Offre commerciale',
        }
        if not self.type: return "Status de type indéfini"
        if self.type not in d: return self.type
        return d[self.type]


    def get_fields_description(self):
        return {
            "_ident": {
                "name": "Identifiant",
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
            "to_profiles": {
                "name": "to_profiles",
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
            "share_count": {
                "name": "share_count",
                "description": ""
            },
            "like_count": {
                "name": "like_count",
                "description": ""
            },
            "comment_count": {
                "name": "comment_count",
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
            raise Exception('A DICT or JSON object must be passed as argument.')

        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)
        removeEmojisFromFields(self,['message', 'description'])
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


class share_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="share_counts")

class FBAttachment(models.Model):
    description = models.TextField(null=True)
    imageUrl = models.CharField(max_length=1024, null=True)
    imageUrl = models.CharField(max_length=1024, null=True)
    targetUrl = models.CharField(max_length=1024, null=True)
    title = models.CharField(max_length=512, null=True)
    type = models.CharField(max_length=32, null=True)

    def update(self, jObject):
        if 'description' in jObject:
            self.description = jObject['description']
        if 'media' in jObject and 'image' in jObject['media']:
            if 'url' in jObject['media']['image']:
                self.imageUrl = jObject['media']['image']['url']
            elif 'src' in jObject['media']['image']:
                self.imageUrl = jObject['media']['image']['src']
            else:
                log(jObject['media'])
        if 'target' in jObject:
            self.targetUrl = jObject['target']['url']
        if 'title' in jObject:
            self.title = jObject['title']
        if 'type' in jObject:
            self.type = jObject['type']
        self.save()

class FBComment(GenericModel):
    reference_name = 'fbComment'

    _ident = models.CharField(max_length=255, unique=True)
    from_profile = models.ForeignKey(FBProfile,related_name="posted_comments", null=True)
    attachment = models.OneToOneField(FBAttachment, related_name="fbComments", null=True)
    created_time = models.DateTimeField(null=True)
    deleted_time = models.DateTimeField(null=True)
    message = models.TextField(null=True)
    permalink_url = models.CharField(max_length=1024,null=True)
    parentPost = models.ForeignKey(FBPost,related_name="fbComments", null=True)
    parentComment = models.ForeignKey("self",related_name="fbReplies", null=True)

    ### Statistics fields ###
    comment_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)

    ### Management fields ###
    last_reaction_harvested = models.DateTimeField(null=True)
    last_comments_harvested = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(null=True)
    error_on_update = models.BooleanField(default=False)
    error_on_harvest = models.BooleanField(default=False)

    ### Utils ###

    def __str__(self):
        if self.parentPost:
            return "Commentaire de %s's sur %s"%(self.from_profile, self.parentPost)
        elif self.parentComment:
            return "Réponse de %s's à propos de %s"%(self.from_profile, self.parentComment)
    def getStr(self):
        return str(self)

    def getParent(self):
        if self.parentPost:
            return str(self.parentPost), "/facebook/post/%s"%self.parentPost.pk
        elif self.parentComment:
            return str(self.parentComment), "/facebook/comment/%s"%self.parentComment.pk

    def get_fields_description(self):
        return {
            "_ident":{
                "name":"_ident",
                "description":""
            },
            "from_profile":{
                "name":"from_profile",
                "description":""
            },
            "attachment":{
                "name":"attachment",
                "description":""
            },
            "created_time":{
                "name":"created_time",
                "description":""
            },
            "deleted_time":{
                "name":"deleted_time",
                "description":""
            },
            "message":{
                "name":"message",
                "description":""
            },
            "permalink_url":{
                "name":"permalink_url",
                "description":""
            },
            "parentPost":{
                "name":"parentPost",
                "description":""
            },
            "parentComment":{
                "name":"parentComment",
                "description":""
            },
            "comment_count":{
                "name":"comment_count",
                "description":""
            },
            "like_count":{
                "name":"like_count",
                "description":""
            },
        }

    ### Update routine ###
    basicFields = {
        "created_time":['created_time'],
        "message":['message'],
        "permalink_url":['permalink_url'],
        "comment_count": ['comment_count'],
        "like_count": ['like_count'],
    }
    statistics = {
        "comment_counts": ['comment_count'],
        "like_counts": ['like_count'],
    }
    def update(self, jObject):
        super(FBComment, self).update(jObject)
        self.setAttachement(jObject)
        self.last_updated = today()
        removeEmojisFromFields(self, ['message',])
        self.save()

    def setAttachement(self, jObject):
        if "attachment" in jObject:
            if not self.attachment:
                self.attachment = FBAttachment.objects.create()
            self.attachment.update(jObject['attachment'])


class like_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="like_counts",null=True)
    fbComment = models.ForeignKey(FBComment, related_name="like_counts",null=True)
class comment_count(Integer_time_label):
    fbPost = models.ForeignKey(FBPost, related_name="comment_counts",null=True)
    fbComment = models.ForeignKey(FBComment, related_name="comment_counts",null=True)


class FBReaction(GenericModel):
    from_profile = models.ForeignKey(FBProfile, related_name="reacted_to")
    to_post = models.ForeignKey(FBPost, related_name="reactions",null=True)
    to_comment = models.ForeignKey(FBComment, related_name="reactions", null=True)
    type = models.CharField(max_length=10, default="LIKE")
    from_time = models.DateTimeField(default=djangoNow)
    until_time = models.DateTimeField(null=True)

    def get_fields_description(self):
        return {
            "from_profile":{
                "name":"from_profile",
                "description":""
            },
            "to_post":{
                "name":"to_post",
                "description":""
            },
            "to_comment":{
                "name":"to_comment",
                "description":""
            },
            "type":{
                "name":"type",
                "description":""
            },
            "from_time":{
                "name":"from_time",
                "description":""
            },
            "until_time":{
                "name":"until_time",
                "description":""
            },
        }
