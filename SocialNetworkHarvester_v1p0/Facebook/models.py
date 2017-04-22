from django.db import models
import requests, time, re
from SocialNetworkHarvester_v1p0.models import *
from SocialNetworkHarvester_v1p0.settings import facebookLogger, DEBUG, FACEBOOK_APP_PARAMS

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
    display_subtext = models.CharField(max_length=1024, null=True)
    displayed_message_response_time = models.CharField(max_length=128, null=True)
    emails = models.CharField(max_length=1024, null=True)
    featured_video = models.CharField(max_length=1024, null=True) #TODO: keep only the URL of the video
    general_info = models.TextField( null=True)
    impressum = models.CharField(max_length=128, null=True)
    link = models.CharField(max_length=128, null=True)
    members = models.TextField(null=True)
    is_community_page = models.BooleanField(default=False)
    is_unclaimed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    location = models.ForeignKey(FBLocation, null=True)
    parent_page = models.ForeignKey('self', null=True)
    phone = models.CharField(max_length=64, null=True)
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
    merchant_id = models.TextField(null=True)
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
            "display_subtext": {
                "name": "display_subtext",
                "description": ""
            },
            "displayed_message_response_time": {
                "name": "displayed_message_response_time",
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
            "impressum": {
                "name": "impressum",
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
            "merchant_id": {
                "name": "merchant_id",
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
        return "FBPage__%s"%self._ident


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

