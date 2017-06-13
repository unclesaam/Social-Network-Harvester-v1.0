""" ############ DEPRECATED #############


from AspiraUser.models import getUserSelection
from Twitter.models import *
import time
from django.http import Http404

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


def TWselectBase(request):
    tableIdsFunctions = {
        'TWTweetTable': TWTweetTableSelection,
        'TWHashtagTable': TWHashtagTableSelection,
        'TWUserTable': TWUserTableSelection,
        'TWUserTweetTable': TWUserTweetTableSelection,
        'TWUserMentionsTable': TWUserMentionsTableSelection,
        'TWFollowersTable': TWFollowersTableSelection,
        'TWFriendsTable': TWFriendsTableSelection,
        'TWUserFavoritesTable': TWUserFavoritesTableSelection,
        'HashtagTweetTable': HashtagTweetTableSelection,
        'TWRetweetTable': TWRetweetTableSelection,
        'TWMentionnedUsersTable': TWMentionnedUsersTableSelection,
        'TWFavoritedByTable': TWFavoritedByTableSelection,
        'TWContainedHashtagsTable': TWContainedHashtagsTableSelection,
        'LinechartTWUserTable': TWUserTableSelection,
        'TWTweetRepliesTable': TWRepliesTableSelection,
        'TWUserTableFollowerLoc': TWUserTableSelection,
        'TWUserTableFollowerLoc': TWUserTableSelection,
    }
    return tableIdsFunctions[request.GET['tableId']](request)


########### MAIN TWITTER PAGE #############

# @viewsLogger.debug(showArgs=False)
def TWTweetTableSelection(request):
    '''
    :param select: Boolean. If true, select all item in given table
    :return: None
    '''
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    queryset = Tweet.objects.none()
    if select:
        selectedTWUsers = tableRowsSelection.getSavedQueryset('TWUser', 'TWUserTable')
        selectedHashHarvesters = tableRowsSelection.getSavedQueryset('HashtagHarvester', 'TWHashtagTable')
        for selected in selectedTWUsers:
            queryset = queryset | selected.tweets.all()
        for selected in selectedHashHarvesters:
            queryset = queryset | selected.hashtag.tweets.all()
        options = tableRowsSelection.getQueryOptions(request.GET['tableId'])
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
        queryset = queryset.filter(created_at__isnull=False)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


# @viewsLogger.debug(showArgs=False)
def TWHashtagTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    if select:
        if user.is_staff:
            queryset = HashtagHarvester.objects.filter(harvested_by__isnull=False)
        else:
            queryset = user.userProfile.twitterHashtagsToHarvest.all()
    else:
        queryset = HashtagHarvester.objects.none()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


# @viewsLogger.debug(showArgs=False)
def TWUserTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    user = request.user
    queryset = TWUser.objects.none()
    if select:
        if user.is_staff:
            queryset = TWUser.objects.filter(harvested_by__isnull=False)
        else:
            queryset = user.userProfile.twitterUsersToHarvest.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


########### TWUSER PAGE #############

@viewsLogger.debug(showArgs=False)
def TWUserTweetTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    twuser_ident = request.GET['pageURL'].split('/')[-1]
    twuser = get_from_any_or_404(TWUser, screen_name=twuser_ident,
                                 _ident=twuser_ident, pk=twuser_ident)
    queryset = Tweet.objects.none()
    if select:
        queryset = twuser.tweets.all()
        options = tableRowsSelection.getQueryOptions(request.GET['tableId'])
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def TWUserMentionsTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    twuser_ident = request.GET['pageURL'].split('/')[-1]
    twuser = get_from_any_or_404(TWUser, screen_name=twuser_ident,
                                 _ident=twuser_ident, pk=twuser_ident)
    queryset = Tweet.objects.none()
    if select:
        queryset = twuser.mentions.filter(retweet_of__isnull=True)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def TWFollowersTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    twuser_ident = request.GET['pageURL'].split('/')[-1]
    twuser = get_from_any_or_404(TWUser, screen_name=twuser_ident,
                                 _ident=twuser_ident, pk=twuser_ident)
    queryset = TWUser.objects.none()
    if select:
        queryset = twuser.followers.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def TWFriendsTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    twuser_ident = request.GET['pageURL'].split('/')[-1]
    twuser = get_from_any_or_404(TWUser, screen_name=twuser_ident,
                                 _ident=twuser_ident, pk=twuser_ident)
    queryset = TWUser.objects.none()
    if select:
        queryset = twuser.friends.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def TWUserFavoritesTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    twuser_ident = request.GET['pageURL'].split('/')[-1]
    twuser = get_from_any_or_404(TWUser, screen_name=twuser_ident,
                                 _ident=twuser_ident, pk=twuser_ident)
    queryset = Tweet.objects.none()
    if select:
        queryset = twuser.favorite_tweets.all()
        options = tableRowsSelection.getQueryOptions(request.GET['tableId'])
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(value__retweet_of__isnull=True)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


########### HASHTAG PAGE #############

def HashtagTweetTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    hashtag = get_from_any_or_404(Hashtag, term=value)
    queryset = Tweet.objects.none()
    if select:
        queryset = hashtag.tweets.all()
        options = tableRowsSelection.getQueryOptions(request.GET['tableId'])
        if 'exclude_retweets' in options and options['exclude_retweets']:
            queryset = queryset.filter(retweet_of__isnull=True)
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


########### TWEET PAGE #############

def TWRetweetTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    value = re.sub('_','',value)
    tweet = get_from_any_or_404(Tweet, _ident=value)
    queryset = Tweet.objects.none()
    if select:
        queryset = tweet.retweets.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])


def TWRepliesTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    value = re.sub('_', '', value)
    tweet = get_from_any_or_404(Tweet, _ident=value)
    queryset = Tweet.objects.none()
    if select:
        queryset = tweet.replied_by.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])

def TWMentionnedUsersTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    tweet = get_from_any_or_404(Tweet, _ident=value)
    queryset = Tweet.objects.none()
    if select:
        queryset = tweet.user_mentions.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])

def TWFavoritedByTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    tweet = get_from_any_or_404(Tweet, _ident=value)
    queryset = favorite_tweet.objects.none()
    if select:
        queryset = tweet.favorited_by.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])

def TWContainedHashtagsTableSelection(request):
    select = 'selected' in request.GET
    tableRowsSelection = getUserSelection(request)
    value = request.GET['pageURL'].split('/')[-1]
    tweet = get_from_any_or_404(Tweet, _ident=value)
    queryset = Hashtag.objects.none()
    if select:
        queryset = tweet.hashtags.all()
    tableRowsSelection.saveQuerySet(queryset, request.GET['tableId'])



# @viewsLogger.debug(showArgs=True)
def get_from_any_or_404(table, **kwargs):
    kwargs = {kwarg: kwargs[kwarg] for kwarg in kwargs.keys() if kwargs[kwarg]}  # eliminate "None" values
    item = None
    for param in kwargs.keys():
        if item: break
        try:
            item = table.objects.get(**{param: kwargs[param]})
        except:
            continue
    if not item: raise Http404()
    return item

"""