from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Twitter.models import *
from Youtube.models import YTChannel, YTVideo, YTPlaylist, YTPlaylistItem, YTComment
from Facebook.models import FBPage, FBPost, FBComment
import re, time, pickle, facebook
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG, FACEBOOK_APP_PARAMS
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
    twitterUsersToHarvest = models.ManyToManyField(TWUser, related_name="harvested_by", blank=True)
    twitterUsersToHarvestLimit = models.IntegerField(default=30, blank=True)
    twitterHashtagsToHarvest = models.ManyToManyField(HashtagHarvester, related_name="harvested_by", blank=True)
    twitterHashtagToHarvestLimit = models.IntegerField(default=5, blank=True)

    facebookApp_parameters_error = models.BooleanField(default=False)
    facebookPagesToHarvest = models.ManyToManyField(FBPage, related_name="harvested_by", blank=True)
    facebookPagesToHarvestLimit = models.IntegerField(default=20, blank=True)

    youtubeApp_dev_key = models.CharField(max_length=255, null=True, blank=True)
    youtubeApp_parameters_error = models.BooleanField(default=False)
    ytChannelsToHarvest = models.ManyToManyField(YTChannel, related_name="harvested_by", blank=True)
    ytChannelsToHarvestLimit = models.IntegerField(default=100, blank=True)
    ytPlaylistsToHarvest = models.ManyToManyField(YTPlaylist, related_name="harvested_by", blank=True)
    ytPlaylistsToHarvestLimit = models.IntegerField(default=5, blank=True)

    @staticmethod
    def getHarvestables():
        return {
            'TWUser':'twitterUsersToHarvest',
            'HashtagHarvester':'twitterHashtagsToHarvest',
            'FBPage':'facebookPagesToHarvest',
            'YTChannel':'ytChannelsToHarvest',
            'YTPlaylist':'ytPlaylistsToHarvest',
        }

    def getHarvested(self, modelName, kwargs={}):
        if modelName not in self.harvestableModels(): raise Exception("Wrong model name specified")
        if kwargs:
            return getattr(self, self.harvestableModels()[modelName]).filter(**kwargs)
        return getattr(self, self.harvestableModels()[modelName]).all()


class FBAccessToken(models.Model):
    class Meta:
        app_label = "Facebook"

    _token = models.CharField(max_length=255)
    expires = models.IntegerField(blank=True, null=True)
    # expires gives the "epoch date" of expiration of the token. Compare to time.time() to know if still valid.
    userProfile = models.OneToOneField(UserProfile, related_name="fbAccessToken", null=True)

    def is_expired(self):
        if not self.expires: return True
        return time.time() >= self.expires

    def is_extended(self):
        return self.expires != None

    def __str__(self):
        return "%s's facebook access token"%self.userProfile.user

    def extend(self):
        graph = facebook.GraphAPI(self._token)
        response = graph.extend_access_token(FACEBOOK_APP_PARAMS['app_id'], FACEBOOK_APP_PARAMS['secret_key'])
        if not 'access_token' in response:
            raise Exception("failed to extend access token: %s" % self)
        self._token = response['access_token']
        self.expires = time.time() + int(response['expires_in'])
        self.save()
        log("%s expires in %s seconds"%(self,self.expires-time.time()))


class TableRowsSelection(models.Model):

    class Meta:
        app_label = "AspiraUser"

    user = models.ForeignKey(User, related_name="tableRowsSelections")
    pageUrl = models.CharField(max_length=100)

    def __str__(self):
        return "%s's selection on %s"%(self.user, self.pageUrl)

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
            if not modelName: raise Exception('Must have a modelName argument to create a new query!')
            newQueryset = globals()[modelName].objects.none()
            selectQuery = selectionQuery.objects.create(
                selection_group=self,
                query=pickle.dumps(newQueryset.query),
                model=modelName,
                table_id=table_id)
        else:
            selectQuery = selectQuery[0]
        return selectQuery.getQueryset()

    def getSelectedRowCount(self):
        counts = {}
        for query in self.queries.all():
            counts[query.table_id] = query.getQueryset().distinct().count()
        return counts

    #@viewsLogger.debug(showArgs=True)
    def getQueryOptions(self, tableId):
        query = self.queries.filter(table_id=tableId)
        cleanOptions = {}
        if query.exists():
            options = query[0].miscOptions
            for option in options.split(';'):
                if option != '':
                    key,value = option.split('=')
                    if value == 'True': value = True
                    elif value == 'False': value = False
                    cleanOptions[key] = value
        return cleanOptions

    #@viewsLogger.debug(showArgs=True)
    def setQueryOption(self, tableId, optionName,optionValue):
        query = self.queries.filter(table_id=tableId)
        if query.exists():
            if not optionValue:
                query[0].removeOption(optionName)
            else:
                query[0].addOption(optionName,optionValue)



class selectionQuery(models.Model):
    """Stores a queryset's model name and query commandinstead of the whole queryset.
    """
    selection_group = models.ForeignKey(TableRowsSelection, related_name="queries")
    query = models.BinaryField(max_length=1000)
    model = models.CharField(max_length=25)
    table_id = models.CharField(null=False, max_length=50)
    miscOptions = models.CharField(max_length=1000, default="")

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

    def addOption(self, optionName, optionValue=True):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;"%optionName, "", currentOptions)
        currentOptions += "%s=%s;" % (optionName, optionValue)
        self.miscOptions = currentOptions
        self.save()

    def removeOption(self, optionName):
        currentOptions = self.miscOptions
        if optionName in currentOptions:
            currentOptions = re.sub(r"%s=[^;]+;" % optionName, "", currentOptions)
        self.miscOptions = currentOptions
        self.save()

    def getOptionValue(self, optionName):
        currentOptions = self.miscOptions
        if not optionName in currentOptions:
            return None
        return re.match(r'%s=(?:[^;]+);' % optionName, currentOptions)


#@viewsLogger.debug(showArgs=True)
def getUserSelection(request):
    user = request.user
    pageURL = request.path
    if 'pageURL' in request.GET:
        pageURL = request.GET['pageURL']
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
    selection = TableRowsSelection.objects.filter(user=user, pageUrl=pageURL)
    if selection.exists():
        selection[0].delete()
        TableRowsSelection.objects.create(user=user, pageUrl=pageURL)
