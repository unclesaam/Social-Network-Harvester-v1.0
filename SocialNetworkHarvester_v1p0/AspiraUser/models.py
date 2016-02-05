from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Twitter.models import TWUser, Tweet, Hashtag

class UserProfile(models.Model):

    user = models.OneToOneField(User, related_name="userProfile", null=False)

    twitterApp_consumerKey = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_consumer_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_key = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_secret = models.CharField(max_length=255, null=True, blank=True)

    facebookApp_id = models.CharField(max_length=255, null=True, blank=True)
    facebookApp_secret = models.CharField(max_length=255, null=True, blank=True)
    facebookApp_namespace = models.CharField(max_length=255, null=True, blank=True)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)

    #facebookUsersToHarvest = models.ManyToManyField(FBUser, related_name="belongs_to_users")
    #youtubeUsersToHarvest = models.ManyToManyField(YTUser, related_name="belongs_to_users")
    twitterUsersToHarvest = models.ManyToManyField(TWUser, related_name="belongs_to_users", blank=True)

    _last_tw_update = models.DateTimeField(null=True, blank=True)
    _last_fb_update = models.DateTimeField(null=True, blank=True)
    _last_yt_update = models.DateTimeField(null=True, blank=True)
   # _last_dm_update = models.DateTimeField(null=True)


    def __str__(self):
        return "%s's user profile"%self.user


