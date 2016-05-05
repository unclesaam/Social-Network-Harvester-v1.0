from Twitter.ajax import *


@login_required()
def twitterBaseView(request):
    context = RequestContext(request, {
        'user': request.user,
        "navigator":[
            ("Twitter", "/twitter"),
        ]
    })
    return render_to_response('Twitter/TwitterBase.html', context)

def twUserView(request, TWUser_value):

    twUser = TWUser.objects.filter(screen_name=TWUser_value)
    if not twUser:
        try:
            twUser = TWUser.objects.filter(_ident=TWUser_value)
        except:
            pass
    if not twUser:
        try:
            twUser = TWUser.objects.filter(pk=TWUser_value)
        except:
            pass
    if not twUser:
        raise Http404('No TWUser matches that value')
    twUser = twUser[0]
    context = RequestContext(request, {
        'user': request.user,
        'twUser':twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/"+TWUser_value),
        ],
    })
    if 'snippet' in request.GET and request.GET['snippet'] == 'true':
        return render_to_response('Twitter/TwitterUserSnip.html', context)
    else:
        return render_to_response('Twitter/TwitterUser.html', context)

def twHashtagView(request, TWHashtagTerm):
    hashtag = get_object_or_404(Hashtag, term=TWHashtagTerm)
    context = RequestContext(request, {
        'user': request.user,
        'hashtag': hashtag,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(hashtag), "#"),
        ],
    })
    return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    tweet = get_object_or_404(Tweet, _ident=tweetId)
    twUser = tweet.user
    context = RequestContext(request, {
        'user': request.user,
        'tweet': tweet,
        'twUser': twUser,
        'navigator': [
            ("Twitter", "/twitter"),
            (str(twUser), "/twitter/user/" + twUser.screen_name),
            ("Tweet", ""),
        ],
    })
    return render_to_response('Twitter/TwitterTweet.html', context)
