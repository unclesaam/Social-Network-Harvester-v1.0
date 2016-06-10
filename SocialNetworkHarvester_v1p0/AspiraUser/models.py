from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Twitter.models import TWUser, Tweet, Hashtag, HashtagHarvester
import re
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


class UserProfile(models.Model):

    class Meta:
        app_label = "AspiraUser"

    def __str__(self):
        return "%s's user profile" % self.user

    user = models.OneToOneField(User, related_name="userProfile", null=False)

    twitterApp_consumerKey = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_consumer_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_key = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_access_token_secret = models.CharField(max_length=255, null=True, blank=True)
    twitterApp_parameters_error = models.BooleanField(default=False)

    facebookApp_id = models.CharField(max_length=255, null=True, blank=True)
    facebookApp_secret = models.CharField(max_length=255, null=True, blank=True)
    facebookApp_namespace = models.CharField(max_length=255, null=True, blank=True)
    facebookApp_parameters_error = models.BooleanField(default=False)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)
    youtubeApp_parameters_error = models.BooleanField(default=False)

    #facebookUsersToHarvest = models.ManyToManyField(FBUser, related_name="harvested_by")
    #youtubeUsersToHarvest = models.ManyToManyField(YTUser, related_name="harvested_by")
    twitterUsersToHarvest = models.ManyToManyField(TWUser, related_name="harvested_by", blank=True)
    twitterUsersToHarvestLimit = models.IntegerField(default=100, blank=True)
    twitterHashtagsToHarvest = models.ManyToManyField(HashtagHarvester, related_name="harvested_by", blank=True)
    twitterHashtagToHarvestLimit = models.IntegerField(default=20, blank=True)



class TableRowsSelection(models.Model):

    class Meta:
        app_label = "AspiraUser"

    user = models.OneToOneField(User, related_name="tableRowsSelection")

    miscOptions = models.CharField(max_length=1000,default="")

    def addOption(self, optionName, optionValue=True):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;"%optionName,"",currentOptions)
        currentOptions+="%s=%s;" % (optionName, optionValue)
        self.miscOptions = currentOptions
        self.save()

    def removeOption(self,optionName):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;" % optionName, "", currentOptions)
        self.miscOptions = currentOptions
        self.save()

    def getOptionValue(self,optionName):
        currentOptions = self.miscOptions
        if not optionName in currentOptions:
            return None
        return re.match(r'%s=(?:[^;]+);'%optionName, currentOptions)

    #@viewsLogger.debug(showArgs=True)
    def selectRow(self, table_id, item):
        itemType = ContentType.objects.get_for_model(item)
        SelectionItem.objects.get_or_create(object_id=item.pk,content_type=itemType,
                    selection_group=self,table_id=table_id)

    #@viewsLogger.debug(showArgs=True)
    def unselectRow(self, table_id, item):
        itemType = ContentType.objects.get_for_model(item)
        selection = self.selecteds.filter(object_id=item.pk,content_type=itemType,
                    selection_group=self,table_id=table_id)
        if selection.exists():
            selection[0].delete()




class SelectionItem(models.Model):
    selection_group = models.ForeignKey(TableRowsSelection, related_name="selecteds")
    table_id = models.CharField(null=False, max_length=50)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')






