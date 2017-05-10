from django.contrib import admin
from django.contrib.auth.models import Group
from AspiraUser.models import *

admin.site.unregister(Group)


@admin.register(UserProfile)
class UserProfileManager(admin.ModelAdmin):
    raw_id_fields = (
        'twitterUsersToHarvest',
        'twitterHashtagsToHarvest',
        'ytChannelsToHarvest',
        'ytPlaylistsToHarvest',
        'facebookPagesToHarvest'
    )
    fieldsets = (
        ('', {
            'fields': (
                'user',
            ),
        }),
        ('Twitter app', {
            'classes': ('collapse', 'closed'),
            'fields' : (
                ('twitterApp_consumerKey','twitterApp_consumer_secret'),
                ('twitterApp_access_token_key','twitterApp_access_token_secret'),
                ('twitterUsersToHarvest', 'twitterUsersToHarvestLimit'),
                ('twitterHashtagsToHarvest','twitterHashtagToHarvestLimit'),
            ),
        }),
        ('Facebook app', {
            'classes': ('collapse', 'closed'),
            'fields': (
                ('facebookPagesToHarvest', 'facebookPagesToHarvestLimit'),
            ),
        }),
        ('Youtube app', {
            'classes': ('collapse', 'closed'),
            'fields' : (
                'youtubeApp_dev_key',
                ('ytChannelsToHarvest','ytChannelsToHarvestLimit'),
                ('ytPlaylistsToHarvest', 'ytPlaylistsToHarvestLimit'),
            ),
        }),
    )
