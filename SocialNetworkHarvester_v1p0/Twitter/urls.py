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
from Twitter.views import *

urlpatterns = [
    # pages
    url(r'^$', twitterBaseView),
    url(r'^user/(?P<TWUser_value>[\w\.]+)$', twUserView),
    url(r'^hashtag/(?P<TWHashtagTerm>[\w\.]+)$', twHashtagView),
    url(r"^tweet/_?(?P<tweetId>\d+)$", twTweetView),
    # forms
    url(r'addUser', addUser),
    url(r'removeSelectedItems', removeSelectedItems),
    url(r'addHashtag', addHashtag),
    #url(r'downloadTable', downloadTable),
    # ajax
    url(r'TWUserTable/(?P<aspiraUserId>\d+)', ajaxTWUserTable),
    url(r'TWHashtagTable/(?P<aspiraUserId>\d+)', ajaxTWHashtagTable),
    url(r'TWTweetTable/', ajaxTWTweetTable),
    url(r'TWUserTweetTable/(?P<TWUserId>\d+)', ajaxTWUserTweetTable),
    url(r'TWUserMentionsTable/(?P<TWUserId>\d+)', ajaxTWUserMentions),
    url(r'TWFollowersTable/(?P<TWUserId>\d+)', ajaxTWFollowersTable),
    url(r'TWFriendsTable/(?P<TWUserId>\d+)', ajaxTWFriendsTable),
    url(r'TWFavoritesTable/(?P<TWUserId>\d+)', ajaxTWFavoritesTable),
    url(r'TWRetweetTable/(?P<TweetId>\d+)', ajaxTWRetweets),
    url(r'TWRepliesTable/(?P<TweetId>\d+)', TWRepliesTable),
    url(r'TWMentionnedUsers/(?P<TweetId>\d+)', TWMentionnedUsers),
    url(r'TWFavoritedBy/(?P<TweetId>\d+)', TWFavoritedBy),
    url(r'TWContainedHashtags/(?P<TweetId>\d+)', TWContainedHashtags),
    url(r'TWHashtagTweetTable/(?P<HashtagId>\d+)', TWHashtagTweetTable),
]






