"""SocialNetworkHarvester_v1p0 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from Twitter.views.pages import *
from Twitter.views.ajax import *
from Twitter.views.forms import *

urlpatterns = [
    # pages
    url(r'^$', twitterBaseView),
    url(r'^(?i)user/(?P<TWUser_value>[\w\.]+)$', twUserView),
    url(r'^(?i)hashtag/(?P<TWHashtagTerm>[\w\.]+)$', twHashtagView),
    url(r"^(?i)tweet/_?(?P<tweetId>\d+)$", twTweetView),
    # forms
    url(r'(?i)addUser', addUser),
    #url(r'removeSelectedItems', removeSelectedItems),
    url(r'(?i)addHashtag', addHashtag),
    #url(r'downloadTable', downloadTable),
    # ajax
    url(r'(?i)TWUserTable/(?P<aspiraUserId>\d+)', ajaxTWUserTable),
    url(r'(?i)TWHashtagTable/(?P<aspiraUserId>\d+)', ajaxTWHashtagTable),
    url(r'(?i)TWTweetTable/', ajaxTWTweetTable),
    url(r'(?i)TWUserTweetTable/(?P<TWUserId>\d+)', ajaxTWUserTweetTable),
    url(r'(?i)TWUserMentionsTable/(?P<TWUserId>\d+)', ajaxTWUserMentions),
    url(r'(?i)TWFollowersTable/(?P<TWUserId>\d+)', ajaxTWFollowersTable),
    url(r'(?i)TWFriendsTable/(?P<TWUserId>\d+)', ajaxTWFriendsTable),
    url(r'(?i)TWFavoritesTable/(?P<TWUserId>\d+)', ajaxTWFavoritesTable),
    url(r'(?i)TWRetweetTable/(?P<TweetId>\d+)', ajaxTWRetweets),
    url(r'(?i)TWRepliesTable/(?P<TweetId>\d+)', TWRepliesTable),
    url(r'(?i)TWMentionnedUsers/(?P<TweetId>\d+)', TWMentionnedUsers),
    url(r'(?i)TWFavoritedBy/(?P<TweetId>\d+)', TWFavoritedBy),
    url(r'(?i)TWContainedHashtags/(?P<TweetId>\d+)', TWContainedHashtags),
    url(r'(?i)TWHashtagTweetTable/(?P<HashtagId>\d+)', TWHashtagTweetTable),
]






