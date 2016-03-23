from django.shortcuts import *
from django.contrib.auth.decorators import login_required
import json

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0

# Create your views here.

@login_required()
def lineChart(request):
    if 'ajax' in request.GET and request.GET['ajax']=='true': return ajax_lineChart(request)
    context = RequestContext(request, {
        'user': request.user,
        'navigator': [
            ("Analysis tools", "#"),
            ("Timeline", "/tool/linechart/"),
        ],
    })
    return render_to_response('tool/lineChartTool.html', context)

@viewsLogger.debug()
def ajax_lineChart(request):
    log("GET: %s"%request.GET)
    reqId = None
    if 'tqx' in request.GET:
        print(request.GET['tqx'])
        reqId = 0
    response = {
        "status": 'ok',
        'reqId':reqId,
        "table": {
            "cols": [
                {'id': 'A','label':'Date','type':'number'},
                {'id': 'B','label':'Mickael Temporao (Tweets)','type':'number'},
                {'id': 'C','label':'BCC (Youtube videos)','type':'number'},
                {'id': 'D','label':'Samuel Cloutier (Facebook statuses)','type':'number'}
            ],
            "rows":[
                {'c':[{'v':1},{'v':37.8},{'v':80.8},]},
                {'c':[{'v':2},{'v':30.9},{'v':69.5},]},
                {'c':[{'v':3},{'v':25.4},{'v':57},]},
                {'c':[{'v':4},{'v':11.7},{'v':18.8},]},
                {'c':[{'v':5},{'v':11.9},{'v':17.6},]},
                {'c':[{'v':6},{'v':8.8},{'v':13.6},]},
                {'c':[{'v':7},{'v':7.6},{'v':12.3},]},
                {'c':[{'v':8},{'v':12.3},{'v':29.2},]},
                {'c':[{'v':9},{'v':16.9},{'v':42.9},]},
                {'c':[{'v':10},{'v':12.8},{'v':30.9},]},
                {'c':[{'v':11},{'v':5.3},{'v':7.9},]},
                {'c':[{'v':12},{'v':6.6},{'v':8.4},]},
                {'c':[{'v':13},{'v':4.8},{'v':25},]},
                {'c':[{'v':14},{'v':4.2},{'v':6.2},]},
                {'c':[{'v':15},{'v':37.8},{'v':80.8},]},
                {'c':[{'v':16},{'v':30.9},{'v':69.5},]},
                {'c':[{'v':17},{'v':25.4},{'v':57},]},
                {'c':[{'v':18},{'v':11.7},{'v':18.8},]},
                {'c':[{'v':19},{'v':11.9},{'v':17.6},]},
                {'c':[{'v':20},{'v':8.8},{'v':13.6},]},
                {'c':[{'v':21},{'v':7.6},{'v':12.3},]},
                {'c':[{'v':22},{'v':12.3},{'v':29.2},]},
                {'c':[{'v':23},{'v':16.9},{'v':42.9},]},
                {'c':[{'v':24},{'v':12.8},{'v':30.9},{'v':-50}]},
                {'c':[{'v':25},{'v':5.3},{'v':7.9},{'v':4.7}]},
                {'c':[{'v':26},{'v':6.6},{'v':8.4},{'v':5.2}]},
                {'c':[{'v':27},{'v':4.8},{'v':6.3},{'v':3.6}]},
                {'c':[{'v':28},{'v':4.2},{'v':6.2},{'v':3.4}]},
                {'c':[{'v':29},{'v':300},{'v':80.8},{'v':41.8}]},
                {'c':[{'v':30},{'v':30.9},{'v':69.5},{'v':32.4}]},
                {'c':[{'v':31},{'v':25.4},{'v':57},{'v':25.7}]},
                {'c':[{'v':32},{'v':11.7},{'v':18.8},{'v':10.5}]},
                {'c':[{'v':33},{'v':11.9},{'v':17.6},{'v':10.4}]},
                {'c':[{'v':34},{'v':8.8},{'v':13.6},{'v':7.7}]},
                {'c':[{'v':35},{'v':7.6},{'v':12.3},{'v':9.6}]},
                {'c':[{'v':36},{'v':12.3},{'v':29.2},{'v':10.6}]},
                {'c':[{'v':37},{'v':16.9},{'v':42.9},{'v':14.8}]},
                {'c':[{'v':38},{'v':12.8},{'v':30.9},{'v':11.6}]},
                {'c':[{'v':39},{'v':5.3},{'v':7.9},{'v':4.7}]},
                {'c':[{'v':40},{'v':6.6},{'v':8.4},{'v':5.2}]},
                {'c':[{'v':41},{'v':4.8},{'v':6.3},{'v':3.6}]},
                {'c':[{'v':42},{'v':4.2},{'v':6.2},{'v':50}]},
                {'c':[{'v':43},{'v':37.8},{'v':80.8},{'v':41.8}]},
                {'c':[{'v':44},{'v':30.9},{'v':69.5},{'v':32.4}]},
                {'c':[{'v':45},{'v':25.4},{'v':57},{'v':25.7}]},
                {'c':[{'v':46},{'v':11.7},{'v':18.8},{'v':10.5}]},
                {'c':[{'v':47},{'v':11.9},{'v':17.6},{'v':10.4}]},
                {'c':[{'v':48},{'v':8.8},{'v':13.6},{'v':7.7}]},
                {'c':[{'v':49},{'v':7.6},{'v':12.3},{'v':9.6}]},
                {'c':[{'v':50},{'v':12.3},{'v':29.2},{'v':10.6}]}
            ]
        }
    }
    return HttpResponse("google.visualization.Query.setResponse(%s)"%json.dumps(response), content_type='application/json')

@login_required()
def pieChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('pieChart', context)

@login_required()
def geoChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('geoChart', context)

@login_required()
def bubbleChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('bubbleChart', context)

@login_required()
def distributionChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('distributionChart', context)



''' Response table example:
"table": {
            "cols": [
                {'id': 'A','label':'Date','type':'number'},
                {'id': 'B','label':'Mickael Temporao (Tweets)','type':'number'},
                {'id': 'C','label':'BCC (Youtube videos)','type':'number'},
                {'id': 'D','label':'Samuel Cloutier (Facebook statuses)','type':'number'}
            ],
            "rows":[
                {'c':[{'v':1},{'v':37.8},{'v':80.8},]},
                {'c':[{'v':2},{'v':30.9},{'v':69.5},]},
                {'c':[{'v':3},{'v':25.4},{'v':57},]},
                {'c':[{'v':4},{'v':11.7},{'v':18.8},]},
                {'c':[{'v':5},{'v':11.9},{'v':17.6},]},
                {'c':[{'v':6},{'v':8.8},{'v':13.6},]},
                {'c':[{'v':7},{'v':7.6},{'v':12.3},]},
                {'c':[{'v':8},{'v':12.3},{'v':29.2},]},
                {'c':[{'v':9},{'v':16.9},{'v':42.9},]},
                {'c':[{'v':10},{'v':12.8},{'v':30.9},]},
                {'c':[{'v':11},{'v':5.3},{'v':7.9},]},
                {'c':[{'v':12},{'v':6.6},{'v':8.4},]},
                {'c':[{'v':13},{'v':4.8},{'v':25},]},
                {'c':[{'v':14},{'v':4.2},{'v':6.2},]},
                {'c':[{'v':15},{'v':37.8},{'v':80.8},]},
                {'c':[{'v':16},{'v':30.9},{'v':69.5},]},
                {'c':[{'v':17},{'v':25.4},{'v':57},]},
                {'c':[{'v':18},{'v':11.7},{'v':18.8},]},
                {'c':[{'v':19},{'v':11.9},{'v':17.6},]},
                {'c':[{'v':20},{'v':8.8},{'v':13.6},]},
                {'c':[{'v':21},{'v':7.6},{'v':12.3},]},
                {'c':[{'v':22},{'v':12.3},{'v':29.2},]},
                {'c':[{'v':23},{'v':16.9},{'v':42.9},]},
                {'c':[{'v':24},{'v':12.8},{'v':30.9},{'v':-50}]},
                {'c':[{'v':25},{'v':5.3},{'v':7.9},{'v':4.7}]},
                {'c':[{'v':26},{'v':6.6},{'v':8.4},{'v':5.2}]},
                {'c':[{'v':27},{'v':4.8},{'v':6.3},{'v':3.6}]},
                {'c':[{'v':28},{'v':4.2},{'v':6.2},{'v':3.4}]},
                {'c':[{'v':29},{'v':300},{'v':80.8},{'v':41.8}]},
                {'c':[{'v':30},{'v':30.9},{'v':69.5},{'v':32.4}]},
                {'c':[{'v':31},{'v':25.4},{'v':57},{'v':25.7}]},
                {'c':[{'v':32},{'v':11.7},{'v':18.8},{'v':10.5}]},
                {'c':[{'v':33},{'v':11.9},{'v':17.6},{'v':10.4}]},
                {'c':[{'v':34},{'v':8.8},{'v':13.6},{'v':7.7}]},
                {'c':[{'v':35},{'v':7.6},{'v':12.3},{'v':9.6}]},
                {'c':[{'v':36},{'v':12.3},{'v':29.2},{'v':10.6}]},
                {'c':[{'v':37},{'v':16.9},{'v':42.9},{'v':14.8}]},
                {'c':[{'v':38},{'v':12.8},{'v':30.9},{'v':11.6}]},
                {'c':[{'v':39},{'v':5.3},{'v':7.9},{'v':4.7}]},
                {'c':[{'v':40},{'v':6.6},{'v':8.4},{'v':5.2}]},
                {'c':[{'v':41},{'v':4.8},{'v':6.3},{'v':3.6}]},
                {'c':[{'v':42},{'v':4.2},{'v':6.2},{'v':50}]},
                {'c':[{'v':43},{'v':37.8},{'v':80.8},{'v':41.8}]},
                {'c':[{'v':44},{'v':30.9},{'v':69.5},{'v':32.4}]},
                {'c':[{'v':45},{'v':25.4},{'v':57},{'v':25.7}]},
                {'c':[{'v':46},{'v':11.7},{'v':18.8},{'v':10.5}]},
                {'c':[{'v':47},{'v':11.9},{'v':17.6},{'v':10.4}]},
                {'c':[{'v':48},{'v':8.8},{'v':13.6},{'v':7.7}]},
                {'c':[{'v':49},{'v':7.6},{'v':12.3},{'v':9.6}]},
                {'c':[{'v':50},{'v':12.3},{'v':29.2},{'v':10.6}]}
            ]
        }
'''