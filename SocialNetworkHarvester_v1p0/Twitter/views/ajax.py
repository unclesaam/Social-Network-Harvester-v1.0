from django.shortcuts import *
import json
from django.http import StreamingHttpResponse
from django.db.models import Count
from django.contrib.auth.models import User
from Twitter.models import TWUser, Tweet, Hashtag, follower, HashtagHarvester
from datetime import datetime
import re
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection, resetUserSelection
from SocialNetworkHarvester_v1p0.jsonResponses import *
from tool.views.ajaxTables import *

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0







######### MAIN PAGE #######
@login_required()
def ajaxTWUserTable(request, aspiraUserId):
    aspiraUser = request.user
    if aspiraUser.is_staff:
        queryset = TWUser.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterUsersToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("TWUser", 'TWUserTable')
    return ajaxResponse(queryset, request, selecteds)

@login_required()
def ajaxTWHashtagTable(request, aspiraUserId):
    aspiraUser = User.objects.get(pk=aspiraUserId)
    if aspiraUser.is_staff:
        queryset = HashtagHarvester.objects.filter(harvested_by__isnull=False)
    else:
        queryset = aspiraUser.userProfile.twitterHashtagsToHarvest.all()
    tableRowsSelections = getUserSelection(request)
    selecteds = tableRowsSelections.getSavedQueryset("HashtagHarvester", 'TWHashtagTable')
    return ajaxResponse(queryset, request, selecteds)

@login_required()
def ajaxTWTweetTable(request):
    try:
        #queryset = Tweet.objects.none()
        userSelection = getUserSelection(request)
        selectedTWUsers = userSelection.getSavedQueryset('TWUser', 'TWUserTable')
        selectedHashHarvesters = userSelection.getSavedQueryset('HashtagHarvester', 'TWHashtagTable')
        queryset = userSelection.getSavedQueryset('Tweet', 'TWTweetTable')
        options = userSelection.getQueryOptions('TWTweetTable')
        for user in selectedTWUsers.all():
            queryset = queryset | user.tweets.all()
        for hashtagHarvester in selectedHashHarvesters.all():
            queryset = queryset | hashtagHarvester.hashtag.tweets.all()
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        queryset = queryset.filter(created_at__isnull=False)
        selecteds = userSelection.getSavedQueryset("Tweet", 'TWTweetTable')
        return ajaxResponse(queryset.distinct(), request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWTweetTable:")
        return jsonUnknownError(request)


####### TWUSER PAGE ########
@login_required()
def ajaxTWUserTweetTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWUserTweetTable')
        options = tableRowsSelections.getQueryOptions('TWUserTweetTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)

@login_required()
def ajaxTWUserMentions(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.mentions.filter(retweet_of__isnull=True)
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWUserMentionsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)

@login_required()
def ajaxTWFollowersTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.followers.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("follower", 'TWFollowersTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)

@login_required()
def ajaxTWFriendsTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.friends.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("follower", 'TWFriendsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)

@login_required()
def ajaxTWFavoritesTable(request, TWUserId):
    try:
        twUser = get_object_or_404(TWUser, pk=TWUserId)
        queryset = twUser.favorite_tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("favorite_tweet", 'TWUserFavoritesTable')
        options = tableRowsSelections.getQueryOptions('TWUserFavoritesTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(value__retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)


####### TWEET PAGE #######
@login_required()
def ajaxTWRetweets(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.retweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWRetweetTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWRetweets:")
        return jsonUnknownError(request)

@login_required()
def TWMentionnedUsers(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.user_mentions.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("TWUser", 'TWMentionnedUsersTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return jsonUnknownError(request)

@login_required()
def TWFavoritedBy(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.favorited_by.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("favorite_tweet", 'TWFavoritedByTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return jsonUnknownError(request)

@login_required()
def TWContainedHashtags(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.hashtags.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Hashtag", 'TWContainedHashtagsTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return jsonUnknownError(request)

@login_required()
def TWHashtagTweetTable(request, HashtagId):
    try:
        hashag = get_object_or_404(Hashtag, pk=HashtagId)
        queryset = hashag.tweets.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'HashtagTweetTable')
        options = tableRowsSelections.getQueryOptions('HashtagTweetTable')
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in ajaxTWUserMentions:")
        return jsonUnknownError(request)


@login_required()
def TWRepliesTable(request, TweetId):
    try:
        tweet = get_object_or_404(Tweet, pk=TweetId)
        queryset = tweet.replied_by.all()
        tableRowsSelections = getUserSelection(request)
        selecteds = tableRowsSelections.getSavedQueryset("Tweet", 'TWTweetRepliesTable')
        return ajaxResponse(queryset, request, selecteds)
    except:
        viewsLogger.exception("Error occured in TWMentionnedUsers:")
        return jsonUnknownError(request)

