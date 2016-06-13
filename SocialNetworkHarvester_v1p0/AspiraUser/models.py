from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Twitter.models import *
import re
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import pickle

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

    user = models.ForeignKey(User, related_name="tableRowsSelections")
    pageUrl = models.CharField(max_length=100)
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
    def selectRow(self, table_id, queryset):
        oldQueryset = self.getSavedQueryset(queryset.model._meta.object_name, table_id)
        newQueryset = oldQueryset | queryset
        self.saveQuerySet(newQueryset, table_id)


    #@viewsLogger.debug(showArgs=True)
    def unselectRow(self, table_id, queryset):
        oldQueryset = self.getSavedQueryset(queryset.model._meta.object_name, table_id)
        newQueryset = oldQueryset.exclude(pk__in=queryset)
        self.saveQuerySet(newQueryset, table_id)

    #@viewsLogger.debug(showArgs=True)
    def saveQuerySet(self, queryset, table_id):
        selectQuery = self.queries.filter(table_id=table_id)
        if not selectQuery.exists():
            selectQuery = selectionQuery.objects.create(
                selection_group=self,
                query=pickle.dumps(queryset.query),
                model=queryset.model._meta.object_name,
                table_id=table_id)
        else:
            selectQuery = selectQuery[0]
            selectQuery.setQueryset(queryset)

    #@viewsLogger.debug(showArgs=True)
    def getSavedQueryset(self, modelName, table_id):
        selectQuery = self.queries.filter(table_id=table_id)
        if not selectQuery.exists():
            newQueryset = globals()[modelName].objects.none()
            selectQuery = selectionQuery.objects.create(
                selection_group=self,
                query=pickle.dumps(newQueryset.query),
                model=modelName,
                table_id=table_id)
        else:
            selectQuery = selectQuery[0]
        return selectQuery.getQueryset()


class selectionQuery(models.Model):
    """Stores a queryset's model and query instead of the whole queryset.
    """
    selection_group = models.ForeignKey(TableRowsSelection, related_name="queries")
    query = models.BinaryField(max_length=1000)
    model = models.CharField(max_length=25)
    table_id = models.CharField(null=False, max_length=50)

    def __str__(self):
        return '%s\'s selectionQuery'%self.model

    #@viewsLogger.debug(showArgs=True)
    def getQueryset(self):
        query = pickle.loads(self.query)
        queryset = globals()[self.model].objects.none()
        queryset.query = query
        return queryset

    #@viewsLogger.debug(showArgs=True)
    def setQueryset(self,queryset):
        self.query = pickle.dumps(queryset.query)
        self.save()


# @viewsLogger.debug(showArgs=True)
def getUserSelection(request):
    user = request.user
    pageURL = request.path
    if 'pageURL' in request.GET:
        pageURL = request.GET['pageURL']
    #log('pageURL:%s' % pageURL)
    selection = TableRowsSelection.objects.filter(user=user, pageUrl=pageURL)
    if not selection.exists():
        selection = TableRowsSelection.objects.create(user=user, pageUrl=pageURL)
    return user.tableRowsSelections.get(pageUrl=pageURL)


# @viewsLogger.debug(showArgs=False)
def resetUserSelection(request):
    user = request.user
    pageURL = request.path
    if 'pageURL' in request.GET:
        pageURL = request.GET['pageURL']
    #log('pageURL:%s' % pageURL)
    selection = TableRowsSelection.objects.filter(user=user, pageUrl=pageURL)
    if selection.exists():
        selection[0].delete()
        TableRowsSelection.objects.create(user=user, pageUrl=pageURL)
