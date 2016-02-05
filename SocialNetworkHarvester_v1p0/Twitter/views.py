from django.shortcuts import render_to_response, HttpResponse
import json
from django.contrib.auth.models import User
from SocialNetworkHarvester_v1p0.settings import twitterLogger



def twitterBaseView(request):
    return render_to_response('Twitter/TwitterBase.html')

def twUserView(request, TWUserScreenName):
    context = {
        'user_screen_name':TWUserScreenName,
    }
    return render_to_response('Twitter/TwitterUser.html', context)

def twHashtagView(request, TWHashtagTerm):
    context = {
        'hashtag_term':TWHashtagTerm,
    }
    return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
    context = {
        'tweet_id': tweetId,
    }
    return render_to_response('Twitter/TwitterTweet.html', context)


def ajaxTWUserTable(request, aspiraUserId):
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    else:
        fields = ["screen_name"]
    aUserProfile = User.objects.get(pk=aspiraUserId).userProfile
    aData = []
    for twUser in aUserProfile.twitterUsersToHarvest.all():
        line = ['']
        for attr in fields:
            line.append(getattr(twUser,attr))
        aData.append(line)
    response = {"aaData":aData}
    return HttpResponse(json.dumps(response), content_type='application/json')

def ajaxTWHashtagTable(request, aspiraUserId):
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
        response = {"aaData": [["","fitzgrant",49  ],["","whitehats",73  ],["","olitzforever",143  ],["","olitz",8622  ],["","ScandalHeads",0  ],["","OliviaPope",3230  ],["","TGIT",104161  ],["","ScandalPremiere",2359  ],["","ItsHandled",869  ],["","Gladiators",3954  ],["","AskScandal",352  ],["","ScandalABC",17551  ],["","Scandal",157305  ],["","polcan",39840  ],["","fed2015",19492  ],["","elxn42",366703  ],["","cdnpoli",462074  ],["","abvote",66976  ],["","GregClark4AB",2  ],["","AlbertaParty",117  ],["","davidswann",15  ],["","AlbertaLiberals",6  ],["","RachelNotley",149  ],["","albertaNDP",132  ],["","BrianJeanWRP",2  ],["","TeamWildrose",9  ],["","JimPrentice",260  ],["","PC_Alberta",9  ],["","MikeSchreiner",9  ],["","OntarioGreens",23  ],["","AndreaHorwath",243  ],["","OntarioNDP",46  ],["","Timhudak",1358  ],["","OntarioPCParty",29  ],["","Kathleen_Wynne",38  ],["","OntLiberal",56  ],["","SolZanetti",5  ],["","OptionNationale",49  ],["","AFontecillaQS",0  ],["","FrancoiseDavid",180  ],["","QuebecSolidaire",347  ],["","francoislegault",130  ],["","coalitionavenir",3  ],["","partiquebecois ",260  ],["","phcouillard",261  ],["","LiberalQuebec",30  ],["","Philippe Couillard",18  ],["","Libéral",4341  ]]}
    return HttpResponse(json.dumps(response), content_type='application/json')

def ajaxTWTweetTable(request, aspiraUserId):
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    response = {"aaData": [['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],['', 1036526, '12/56/2015','lindsay_moore15','this is a tweet!', 56],]}
    return HttpResponse(json.dumps(response), content_type='application/json')
