from django.shortcuts import *
import json


def facebookBase(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('facebook/FacebookBase.html', context)


def fbUserView(request, FBUserScreenName):
    context = RequestContext(request, {
        'user': request.user,
        'user_screen_name': FBUserScreenName,
    })
    return render_to_response('Facebook/FacebookUser.html', context)


def fbPostView(request, FBPostId):
    context = RequestContext(request, {
        'user': request.user,
        'postID': FBPostId,
    })
    return render_to_response('Facebook/FacebookPost.html', context)


def fbCommentView(request, FBCommentId):
    context = RequestContext(request, {
        'user': request.user,
        'commentId': FBCommentId,
    })
    return render_to_response('Facebook/FacebookComment.html', context)


# ajax responses
def ajaxFbUserTable(request, aspiraUserId):
    response = {"aaData": [["", "Sol Zanetti", "sol.zanetti.3", "None", "None"],
                           ["", "Option nationale", "OptionNationale.QC", "32086",
                            "Option nationale est un parti politique dont l'objectif est de réaliser l'indépendance du Québec.\n\nLe chef d'Option nationale est monsieur Sol Zanetti"],
                           ["", "Andrés Fontecilla", "AFontecillaQS", "2175",
                            "Co-porte-parole et président de Québec solidaire."],
                           ["", "Françoise David", "FrancoiseDavid.QS", "49893",
                            "Députée de Gouin et porte-parole Québec solidaire. Les mises à jour et interventions sur cette page sont faites par Julien R., Marilyn O. et Jérémie B.W."],
                           ["", "Québec solidaire", "Quebecsolidaire", "65124",
                            "Québec solidaire est un parti politique québécois. Son programme défend une vision écologiste, progressiste, démocrate, féministe, altermondialiste, pluraliste et souverainiste pour l'avenir du Québec."],
                           ["", "François Legault", "FrancoisLegaultPageOfficielle", "17798",
                            "Député de l'Assomption et chef de la Coalition Avenir Québec - Suivez l'actualité de la CAQ sur www.lacaq.org Retrouvez moi aussi sur www.twitter.com/francoislegault"],
                           ["", "Coalition Avenir Québec", "coalitionavenir", "31083",
                            "Plus d’autonomie pour le Québec, une économie plus forte et une meilleure éducation pour nos enfants, c’est aujourd’hui possible !"],
                           ["", "Pauline Marois", "Pauline-Marois", "208", "None"],
                           ["", "Parti Québécois", "lepartiquebecois", "165749",
                            "Le Parti Québécois a comme objectif la souveraineté du Québec.  Joignez-vous à nous!\n\nCette page respecte notre nétiquette: http://pq.org/netiquette/"],
                           ["", "Philippe Couillard", "phcouillard", "31280",
                            "Philippe Couillard est premier ministre du Québec. Ce compte est officiel et animé par l'équipe des communications."],
                           ["", "Parti libéral du Québec", "LiberalQuebec", "37490",
                            "Depuis près de 150 ans, le PLQ est le parti de tous les Québécois.\n\nRèglement ? clic.plq.org/nétiquette-PLQ\n\nContactez-nous ? clic.plq.org/contact-PLQ"]]}
    return HttpResponse(json.dumps(response), content_type='application/json')


def ajaxFbPostTable(request, aspiraUserId):
    response = {"aaData": [["", "fitzgrant", 49], ["", "whitehats", 73], ["", "olitzforever", 143], ["", "olitz", 8622],
                           ["", "ScandalHeads", 0], ["", "OliviaPope", 3230], ["", "TGIT", 104161],
                           ["", "ScandalPremiere", 2359], ["", "ItsHandled", 869], ["", "Gladiators", 3954],
                           ["", "AskScandal", 352], ["", "ScandalABC", 17551], ["", "Scandal", 157305],
                           ["", "polcan", 39840], ["", "fed2015", 19492], ["", "elxn42", 366703],
                           ["", "cdnpoli", 462074], ["", "abvote", 66976], ["", "GregClark4AB", 2],
                           ["", "AlbertaParty", 117], ["", "davidswann", 15], ["", "AlbertaLiberals", 6],
                           ["", "RachelNotley", 149], ["", "albertaNDP", 132], ["", "BrianJeanWRP", 2],
                           ["", "TeamWildrose", 9], ["", "JimPrentice", 260], ["", "PC_Alberta", 9],
                           ["", "MikeSchreiner", 9], ["", "OntarioGreens", 23], ["", "AndreaHorwath", 243],
                           ["", "OntarioNDP", 46], ["", "Timhudak", 1358], ["", "OntarioPCParty", 29],
                           ["", "Kathleen_Wynne", 38], ["", "OntLiberal", 56], ["", "SolZanetti", 5],
                           ["", "OptionNationale", 49], ["", "AFontecillaQS", 0], ["", "FrancoiseDavid", 180],
                           ["", "QuebecSolidaire", 347], ["", "francoislegault", 130], ["", "coalitionavenir", 3],
                           ["", "partiquebecois ", 260], ["", "phcouillard", 261], ["", "LiberalQuebec", 30],
                           ["", "Philippe Couillard", 18], ["", "Libéral", 4341]]}
    return HttpResponse(json.dumps(response), content_type='application/json')


def ajaxFbCommentTable(request, aspiraUserId):
    response = {"aaData": [['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56],
                           ['', 1036526, '12/56/2015', 'lindsay_moore15', 'this is a tweet!', 56], ]}
    return HttpResponse(json.dumps(response), content_type='application/json')
