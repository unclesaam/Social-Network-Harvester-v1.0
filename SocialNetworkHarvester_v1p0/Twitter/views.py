from django.shortcuts import *
import json

def twitterBaseView(request):
	return render_to_response('Twitter/TwitterBase.html')

def twUserView(request, TWUserScreenName):
	context = {
		'user_screen_name':TWUserScreenName,
	}
	return render_to_response('Twitter/TwitterUser.html', context)

def twHashtagView(request, TWHashtagTem):
	context = {
		'hashtag_term':TWHashtagTem,
	}
	return render_to_response('Twitter/TwitterHashtag.html', context)

def twTweetView(request, tweetId):
	context = {
		'tweet_id': tweetId,
	}
	return render_to_response('Twitter/TwitterTweet.html', context)



	# ajax responses
def ajaxTWUserTable(request, aspiraUserId):
	if 'fields' in request.GET:
		fields = request.GET['fields'].split(',')
	response = {"aaData": [["", "None", "Holmesrd", "None", "None", "None", "None"], ["", "None", "DailyTie", "None", "None", "None", "None"], ["", "None", "alarabobara", "None", "None", "None", "None"], ["", "None", "me_jennaa", "None", "None", "None", "None"], ["", "None", "prettyshortcake", "None", "None", "None", "None"], ["", "None", "julie_kamper", "None", "None", "None", "None"], ["", "None", "melanyrosee_", "None", "None", "None", "None"], ["", "None", "CJBriggs6", "None", "None", "None", "None"], ["", "Dymund", "Loove_Always15", "None", "None", "None", "None"], ["", "None", "sharanda7", "None", "None", "None", "None"], ["", "Champagne", "MiszChampagne", "None", "None", "None", "None"], ["", "None", "SLEdge1213", "None", "None", "None", "None"], ["", "Adele", "Adele", "None", "None", "None", "None"], ["", "None", "alexlartwork", "None", "None", "None", "None"], ["", "None", "jody_macA", "None", "None", "None", "None"], ["", "None", "AMarieEspinosa", "None", "None", "None", "None"], ["", "None", "paulette49", "None", "None", "None", "None"], ["", "None", "eliamagaly", "None", "None", "None", "None"], ["", "None", "mariadixon", "None", "None", "None", "None"], ["", "None", "Gibby1017", "None", "None", "None", "None"], ["", "None", "LSCHWAGR", "None", "None", "None", "None"], ["", "None", "ThrivingCougar", "None", "None", "None", "None"], ["", "None", "Italianbread26", "None", "None", "None", "None"]]}
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