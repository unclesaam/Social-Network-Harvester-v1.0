from AspiraUser.views import addMessagesToContext
from Twitter.views.ajax import *
from Twitter.views.tableSelections import *

@login_required()
def twitterBaseView(request):
    context = {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    }
    request, context = addMessagesToContext(request, context)
    resetUserSelection(request)
    return render(request, 'Twitter/TwitterBase.html', context)


@login_required()
def twUserView(request, TWUser_value):
    queryset = TWUser.objects.none();
    try:
        queryset = TWUser.objects.filter(pk=TWUser_value)
    except:
        pass
    if not queryset:
        try:
            queryset = TWUser.objects.filter(screen_name=TWUser_value)
        except:
            pass
    if not queryset:
        try:
            queryset = TWUser.objects.filter(_ident=TWUser_value)
        except:
            pass
    if not queryset:
        raise Http404('No TWUser matches that value')
    twUser = queryset[0]
    context = {
        'user': request.user,
        'twUser':twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/"+TWUser_value),
        ],
    }
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        try:
            return render_to_response('Twitter/TwitterUserSnip.html', context)
        except:
            pass
    else:
        resetUserSelection(request)

        return render(request,'Twitter/TwitterUser.html', context)


@login_required()
def twHashtagView(request, TWHashtagTerm):
    hashtag = get_object_or_404(Hashtag, term=TWHashtagTerm)
    context = {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(hashtag), "#"),
        ],
    }
    resetUserSelection(request)
    return render(request,'Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    tweet = None
    try:
        tweet = Tweet.objects.get(pk=tweetId)
    except:
        pass
    if not tweet:
        tweet = Tweet.objects.get(_ident=tweetId)
    if not tweet:
        raise Http404('No tweet matches that value')
    twUser = tweet.user
    context = {
        'user': request.user,
        'tweet': tweet,
        'twUser': twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            ((str(twUser) if twUser else 'Unidentifed TWUser'),
             ("/twitter/user/" + str(twUser.pk) if twUser else '#')),
            ("Tweet", ""),
        ],
    }
    resetUserSelection(request)
    return render(request,'Twitter/TwitterTweet.html', context)










