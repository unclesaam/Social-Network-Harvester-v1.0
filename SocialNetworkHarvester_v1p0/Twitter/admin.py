from django.contrib import admin
from .models import *


@admin.register(TWUser)
class TWUserManager(admin.ModelAdmin):
    fieldsets = (
        ('', {
            'fields': (
                'screen_name',
                 '_ident'

            ),
        }),
        ('Other infos', {
            'classes': ('collapse', 'closed'),
            'fields' : (
                        'created_at',
                        'geo_enabled',
                        'has_extended_profile',
                        'is_translation_enabled',
                        'is_translator',
                        'lang',
                        'location',
                        'profile_background_color',
                        'profile_background_image_url',
                        'profile_image_url',
                        'protected',
                        'verified',
                        'name',
                        'time_zone',
                        'url',
                        'description',
                        'statuses_count',
                        'favourites_count',
                        'followers_count',
                        'friends_count',
                        'listed_count'
            ),
        }),
    )
    readonly_fields = [
        'created_at',
        'geo_enabled',
        'has_extended_profile',
        'is_translation_enabled',
        'is_translator',
        'lang',
        'location',
        'profile_background_color',
        'profile_background_image_url',
        'profile_image_url',
        'protected',
        'verified',
        'name',
        'time_zone',
        'url',
        'description',
        'statuses_count',
        'favourites_count',
        'followers_count',
        'friends_count',
        'listed_count'
    ]










