from django.shortcuts import *
from django.contrib.auth.decorators import login_required
import json
from Twitter.models import TWUser, Tweet, Hashtag, follower
import re
from django.db.models import Count

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

#@viewsLogger.debug()
def ajax_lineChart(request):
    #log("GET: %s"%request.GET)
    reqId = None
    if 'tqx' in request.GET:
        #log('tqx: %s'%request.GET['tqx'])
        reqId = request.GET['tqx'].split(':')[1]
    try:
        response = {
            "status": 'ok',
            'reqId':reqId,
            "table": generateLineChartTable(request),
        }
    except Exception as e:
        viewsLogger.exception('An error occured while creating a Linechart')
        response = {
            'status':'error',
            'message':e.args[0],
            'reqId':reqId,
        }
    return HttpResponse("google.visualization.Query.setResponse(%s)"%json.dumps(response), content_type='application/json')

#@viewsLogger.debug()
def generateLineChartTable(request):
    if not 'selected_rows' in request.GET:
        return {'cols':[{'label':'','type':'number'},
                        {'label':'Select some data in the tables below (max 10)','type':'number'}],
                'rows':[{'c':[{'v':0},{'v':0}]}]}
    sources = []
    for rowId in request.GET['selected_rows'].split(','):
        if rowId != "":
            obj = getObjectFromSelectedRow(rowId)
            sources.append(obj)
            if len(sources) > 10:
                raise Exception('Please select at most 10 elements or create a group')
    if request.GET['chart_type'] == 'user_activity':
        return linechart_userActivity(sources)
    else:
        raise Exception('Invalid chart_type value')

''' Linechart response table example:
"table": {
            "cols": [
                {'id': 'A','label':'Date','type':'number'},
                {'id': 'B','label':'Mickael Temporao (Tweets)','type':'number'},
                {'id': 'C','label':'BCC (Youtube videos)','type':'number'},
                {'id': 'D','label':'Samuel Cloutier (Facebook statuses)','type':'number'}
                ...
            ],
            "rows":[
                {'c':[{'v':1},{'v':37.8},{'v':80.8},]},
                {'c':[{'v':2},{'v':30.9},{'v':69.5},]},
                {'c':[{'v':3},{'v':25.4},{'v':57},]},
                ...
            ]
        }
'''
#@viewsLogger.debug()
def linechart_userActivity(sources):
    values = {}
    numSource = 0
    cols = [{'label':'Date', 'type':'date'}]
    for source in sources:
        for existingDate in values.keys():
            values[existingDate].append(0)
        if isinstance(source, TWUser):
            cols.append({'label':'%s (Tweets)'%source.name, 'type':'number'})
            dates = source.tweets.extra({'date_created' : "date(created_at)"})\
                .values('date_created')\
                .annotate(date_count=Count('id'))
            for date in dates:
                strDate = str(date['date_created'])
                if strDate not in values:
                    values[strDate] = [0 for i in range(numSource)]+[date['date_count']]
                else:
                    values[strDate][-1] = date['date_count']
            numSource += 1
        elif isinstance(source, Hashtag):
            pass
    #pretty('values: %s'%values)
    rows = []
    for date in sorted(values):
        dateVals = date.split('-')
        row = [{'v':values[date][x]}for x in range(len(values[date]))]
        row.insert(0,{'v':'Date(%i, %i, %i)'%(int(dateVals[0]),int(dateVals[1]),int(dateVals[2]))})
        rows.append({'c':row})
    return {'cols':cols, 'rows':rows}

#@viewsLogger.debug()
def getObjectFromSelectedRow(rowId):
    val = re.match(r'^(?P<type>[^0-9]*)_(?P<id>[0-9]*)',rowId)
    id = val.group('id')
    type = val.group('type')
    if type in ["TWUser", "Hashtag"]:
        className = globals()[type]
        return get_object_or_404(className, pk=id)
    else:
        raise('Invalid class name')


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
