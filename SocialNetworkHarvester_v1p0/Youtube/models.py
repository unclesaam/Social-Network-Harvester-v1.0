from django.db import models
from SocialNetworkHarvester_v1p0.models import Integer_time_label, Image_time_label



####################### YTCHANNEL  #######################

class YTChannel(models.Model):
    _ident = models.CharField(max_length=128,null=True)
    userName = models.CharField(max_length=32, null=True)
    description = models.CharField(max_length=1000, null=True)
    keywords = models.CharField(max_length=1000, null=True)
    profileColor = models.CharField(max_length=16, null=True)
    title = models.CharField(max_length=128, null=True)
    publishedAt = models.DateTimeField(null=True)
    hiddenSubscriberCount = models.BooleanField(default=False)
    isLinked = models.BooleanField(default=False)
    privacyStatus = models.CharField(max_length=32, null=True)
    featuredChannel = models.ManyToManyField('self',related_name='featured_by')
    commentCount = models.IntegerField(null=True)
    subscriberCount = models.IntegerField(null=True)
    videoCount = models.IntegerField(null=True)
    viewCount = models.IntegerField(null=True)

    _deleted_at = models.DateTimeField(null=True)
    _last_updated = models.DateTimeField(null=True)
    _last_video_harvested = models.DateTimeField(null=True)
    _error_on_update = models.BooleanField(default=False)
    _error_on_harvest = models.BooleanField(default=False)
    _update_frequency = models.IntegerField(default=1)  # 1 = every day, 2 = every 2 days, etc.
    _harvest_frequency = models.IntegerField(default=1)
    _has_reached_begining = models.BooleanField(default=False)

    class Meta:
        app_label = "Youtube"

    def __str__(self):
        if self.userName: return self.userName
        if self._ident: return self._ident
        return 'Unidentified YTChannel'

    def get_fields_description(self):
        return {
            '_ident':{
                'name':'Identifier',
                'description':'Unique identifier number of the channel'
            },
            'description': {
                'name': 'Description',
                'description': 'Description of the channel''s content'
            },
            'keywords': {
                'name': 'Keywords',
                'description': 'Key words associated with the channel'
            },
            'profileColor': {
                'name': 'Profile color',
                'description': 'Background color of the channel page'
            },
            'title': {
                'name': 'Title',
                'description': 'Title of the channel'
            },
            'userName': {
                'name': 'Username',
                'description': 'Unique username of the channel, can be changed once by the user. Not permanent'
            },
            'publishedAt': {
                'name': 'Published at',
                'description': 'Creation date of the channel'
            },
            'hiddenSubscriberCount': {
                'name': 'Hidden Subscriber count',
                'description': 'Whether the number of subscribers should be hidden'
            },
            'isLinked': {
                'name': 'Is linked',
                'description': 'Whether the channel is linked to a Google+ account'
            },
            'privacyStatus': {
                'name': 'Privacy status',
                'description': 'Privacy status of the channel. Can be "Private", "Public" or "Unlisted"'
            },
            'featuredChannel': {
                'name': 'Featured channels',
                'description': 'Other channels the user chose to feature in his/her channel'
            },
            'commentCount': {
                'name': 'Comment count',
                'description': 'Number of comments posted by the channel on videos (last recorded)'
            },
            'subscriberCount': {
                'name': 'Subscriber count',
                'description': 'Number of subscribers of the channel (last recorded)'
            },
            'videoCount': {
                'name': 'Video count',
                'description': 'Number of videos hosted on the channel (last recorded)'
            },
            'viewCount': {
                'name': 'View count',
                'description': 'Combined number of views of all the videos on the channel (last recorded)'
            },
        }

    def get_obj_ident(self):
        return "YTChannel__%s" % self.pk

# OBJECT SAMPLE
'''
        { 'brandingSettings': { 'channel': { 'country': 'US',
                                         'defaultLanguage': 'en-GB',
                                         'description': 'Gav and Dan take on the world in Slow Motion!\n'
                                                        '\n'
                                                        'We shoot all of our videos in HD using high-speed cinema cameras and we highly recommend you watch '
                                                        'them that way if you can!\n'
                                                        '\n'
                                                        'For business enquiries, use the link below. All emails are read.\n'
                                                        '\n'
                                                        'Buy our shirts! http://store.roosterteeth.com/search?type=product&q=slow+mo\n'
                                                        '\n'
                                                        '© GAVIN FREE',
                                         'featuredChannelsTitle': '2nd Channel',
                                         'featuredChannelsUrls': ['UCgC4Nn0rqqdeqACnzaIMo_Q'],
                                         'keywords': 'slow mo guys high speed motion super slomo phantom hd gav dan 1000fps gavin free slap smash flex "the '
                                                     'slow mo guys"',
                                         'profileColor': '#000000',
                                         'showBrowseView': True,
                                         'showRelatedChannels': True,
                                         'title': 'The Slow Mo Guys',
                                         'trackingAnalyticsAccountId': 'UA-2631020-13',
                                         'unsubscribedTrailer': 'np68FhljCb8'},
                            'hints': [ { 'property': 'channel.banner.mobile.medium.image.url',
                                         'value': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w640-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg'},
                                       {'property': 'channel.featured_tab.template.string', 'value': 'Everything'},
                                       {'property': 'channel.modules.show_comments.bool', 'value': 'True'}],
                            'image': { 'bannerImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1060-fcrop64=1,00005a57ffffa5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerMobileExtraHdImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1440-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerMobileHdImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1280-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerMobileImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w640-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerMobileLowImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w320-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerMobileMediumHdImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w960-fcrop64=1,32b75a57cd48a5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTabletExtraHdImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w2560-fcrop64=1,00005a57ffffa5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTabletHdImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w2276-fcrop64=1,00005a57ffffa5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTabletImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1707-fcrop64=1,00005a57ffffa5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTabletLowImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1138-fcrop64=1,00005a57ffffa5a8-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTvHighImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1920-fcrop64=1,00000000ffffffff-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTvImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w2120-fcrop64=1,00000000ffffffff-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTvLowImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w854-fcrop64=1,00000000ffffffff-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg',
                                       'bannerTvMediumImageUrl': 'https://yt3.ggpht.com/-pgWyKrihmsw/VDXWh78jSvI/AAAAAAAAAHk/lvfC_CqbF9s/w1280-fcrop64=1,00000000ffffffff-nd-c0xffffffff-rj-k-no/YOUTUBE_SLOMO_GUYS_CHANNEL_IMAGE.jpg'}},
      'contentDetails': { 'relatedPlaylists': { 'favorites': 'FLUK0HBIBWgM2c4vsPhkYY4w',
                                                'likes': 'LLUK0HBIBWgM2c4vsPhkYY4w',
                                                'uploads': 'UUUK0HBIBWgM2c4vsPhkYY4w'}},
      'etag': '"I_8xdZu766_FSaexEaDXTIfEWc0/c7ADrvZeF1ZIAxe1NpcvjNygN7o"',
      'id': 'UCUK0HBIBWgM2c4vsPhkYY4w',
      'kind': 'youtube#channel',
      'localizations': { 'en-GB': { 'description': 'Gav and Dan take on the world in Slow Motion!\n'
                                                   '\n'
                                                   'We shoot all of our videos in HD using high-speed cinema cameras and we highly recommend you watch them '
                                                   'that way if you can!\n'
                                                   '\n'
                                                   'For business enquiries, use the link below. All emails are read.\n'
                                                   '\n'
                                                   'Buy our shirts! http://store.roosterteeth.com/search?type=product&q=slow+mo\n'
                                                   '\n'
                                                   '© GAVIN FREE',
                                    'title': 'The Slow Mo Guys'}},
      'snippet': { 'country': 'US',
                   'defaultLanguage': 'en-GB',
                   'description': 'Gav and Dan take on the world in Slow Motion!\n'
                                  '\n'
                                  'We shoot all of our videos in HD using high-speed cinema cameras and we highly recommend you watch them that way if you '
                                  'can!\n'
                                  '\n'
                                  'For business enquiries, use the link below. All emails are read.\n'
                                  '\n'
                                  'Buy our shirts! http://store.roosterteeth.com/search?type=product&q=slow+mo\n'
                                  '\n'
                                  '© GAVIN FREE',
                   'localized': { 'description': 'Gav and Dan take on the world in Slow Motion!\n'
                                                 '\n'
                                                 'We shoot all of our videos in HD using high-speed cinema cameras and we highly recommend you watch them that '
                                                 'way if you can!\n'
                                                 '\n'
                                                 'For business enquiries, use the link below. All emails are read.\n'
                                                 '\n'
                                                 'Buy our shirts! http://store.roosterteeth.com/search?type=product&q=slow+mo\n'
                                                 '\n'
                                                 '© GAVIN FREE',
                                  'title': 'The Slow Mo Guys'},
                   'publishedAt': '2010-08-15T13:51:49.000Z',
                   'thumbnails': { 'default': { 'url': 'https://yt3.ggpht.com/-hdZED2lNuKE/AAAAAAAAAAI/AAAAAAAAAAA/ppDB-or2f7I/s88-c-k-no-rj-c0xffffff/photo.jpg'},
                                   'high': {'url': 'https://yt3.ggpht.com/-hdZED2lNuKE/AAAAAAAAAAI/AAAAAAAAAAA/ppDB-or2f7I/s240-c-k-no-rj-c0xffffff/photo.jpg'},
                                   'medium': { 'url': 'https://yt3.ggpht.com/-hdZED2lNuKE/AAAAAAAAAAI/AAAAAAAAAAA/ppDB-or2f7I/s240-c-k-no-rj-c0xffffff/photo.jpg'}},
                   'title': 'The Slow Mo Guys'},
      'statistics': {'commentCount': '6303', 'hiddenSubscriberCount': False, 'subscriberCount': '8361609', 'videoCount': '130', 'viewCount': '981364335'},
      'status': {'isLinked': True, 'longUploadsStatus': 'longUploadsUnspecified', 'privacyStatus': 'public'}}
        '''


class CommentCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='comment_counts')

class SubscriberCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='subscriber_counts')

class VideoCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='video_counts')

class ViewCount(Integer_time_label):
    channel = models.ForeignKey(YTChannel, related_name='view_counts')

class ContentImage(Image_time_label):
    channel = models.ForeignKey(YTChannel, related_name='channel_images')


#######################  YTVIDEO  ########################

class YTVideo(models.Model):

    channel = models.ForeignKey(YTChannel, related_name='videos')

    class Meta:
        app_label = "Youtube"

#######################  YTPLAYLIST  #####################

class YTPlaylist(models.Model):

    channel = models.ForeignKey(YTChannel, related_name='playlists')

    class Meta:
        app_label = "Youtube"

    def videos(self):
        return self.items.order_by('playlistOrder').values('video')


class YTPlaylistItem(models.Model):

    playlist = models.ForeignKey(YTPlaylist, related_name='items')
    video = models.ForeignKey(YTVideo, related_name='playlists')
    playlistOrder = models.IntegerField(null=False)

    class Meta:
        app_label = "Youtube"


#######################  YTCOMMENT  ######################

class YTComment(models.Model):

    video = models.ForeignKey(YTVideo, related_name='comments_threads', null=True)
    channel = models.ForeignKey(YTChannel, related_name='comments_threads', null=True)
    parent_comment = models.ForeignKey("self", related_name='replies', null=True)
    author = models.ForeignKey(YTChannel, related_name='posted_comments')

    class Meta:
        app_label = "Youtube"