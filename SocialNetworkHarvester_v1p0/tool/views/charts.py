from django.shortcuts import *
from django.contrib.auth.decorators import login_required
import json
from Twitter.models import TWUser, Tweet, Hashtag, follower, HashtagHarvester
import re
from django.db.models import Count, Max, Min
from AspiraUser.models import getUserSelection, resetUserSelection
import datetime
import operator

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s : viewsLogger.log(s) if DEBUG else 0
pretty = lambda s : viewsLogger.pretty(s) if DEBUG else 0

#########################  LINECHART  #########################
class LinechartGenerator:
    def __init__(self):
        self.table = {
            'cols': [{'label': 'Date', 'type': 'date'}],
            'rows': []
        }
        self.values = {}

    def addColum(self, col):
        self.table['cols'].append(col)

    def formatDates(self, dates):
        '''Inserts zeros beetween non-zero values in a given time-serie.
        '''
        extrapoledDates = {}
        if dates:
            date = min([item['date_created'] for item in dates if item['date_created']])
            lastEntry = max([item['date_created'] for item in dates if item['date_created']])
            while date != lastEntry:
                extrapoledDates[str(date)] = 0
                date += datetime.timedelta(days=1)
            for date in dates:
                strDate = str(date['date_created'])
                extrapoledDates[strDate] = date['date_count']
        return extrapoledDates

    def insertValues(self, vals):
        vals = self.formatDates(vals)
        for existingKey in self.values.keys():
            self.values[existingKey].append(0)
        numSource = len(self.table['cols']) - 2
        for key in vals:
            if key not in self.values:
                self.values[key] = [0 for i in range(numSource)] + [vals[key]]
            else:
                self.values[key][-1] = vals[key]

    def generate(self):
        for date in sorted(self.values):
            if date != "None":
                # log('date: %s'% date)
                dateVals = date.split('-')
                row = [{'v': self.values[date][x]} for x in range(len(self.values[date]))]
                row.insert(0, {'v': 'Date(%i, %i, %i)' % (int(dateVals[0]), int(dateVals[1]) - 1, int(dateVals[2]))})
                self.table['rows'].append({'c': row})
        return self.table

@login_required()
def lineChart(request):
    if 'ajax' in request.GET and request.GET['ajax']=='true': return ajax_lineChart(request)
    context = {
        'user': request.user,
        'navigator': [
            ("Analytique", "#"),
            ("Temporel", "#"),
            (re.sub('_',' ',request.GET['chart_type']), '#')
        ],
        'chart_type': request.GET['chart_type'],
    }
    resetUserSelection(request)
    return render(request,'tool/lineChartTool.html', context)

def ajax_lineChart(request):
    reqId = None
    if 'tqx' in request.GET:
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
    return HttpResponse("google.visualization.Query.setResponse(%s)"%json.dumps(response),
                        content_type='application/json')

def generateLineChartTable(request):
    table = {}
    if request.GET['chart_type'] == 'activite_en_ligne':
        table =  linechart_userActivity(request)
    elif request.GET['chart_type'] == 'popularite_en_ligne':
        table =  linechart_userPopularity(request)
    else:
        raise Exception('Invalid chart_type value')
    if len(table['cols']) == 1:
        table = {'cols': [{'label': '', 'type': 'number'},
                          {'label': 'Sélectionnez des éléments dans les tables ci-dessous (max 10)', 'type': 'number'}],
                 'rows': [{'c': [{'v': 0}, {'v': 0}]}]}
    return table

def linechart_userActivity(request):
    chartGen = LinechartGenerator()
    tableSelection = getUserSelection(request)
    selectedTWUsers = tableSelection.getSavedQueryset('TWUser', 'TWUserTable')
    selectedTWHashHarvs = tableSelection.getSavedQueryset('HashtagHarvester', 'TWHashtagTable')

    if selectedTWHashHarvs.count() + selectedTWUsers.count() > 10:
        raise Exception('Veuillez sélectionner au plus 10 éléments.')

    for source in selectedTWUsers:
        chartGen.addColum({'label': '%s (Tweets)' %
                    (source.name if source.name else source.screen_name),'type': 'number'})
        tweets = source.tweets.exclude(created_at__isnull=True)
        chartGen.insertValues(tweets.extra({'date_created': "date(created_at)"}) \
                              .values('date_created') \
                              .annotate(date_count=Count('id')))

    for source in selectedTWHashHarvs:
        chartGen.addColum({'label': '#%s (Tweets)' % source.hashtag.term, 'type': 'number'})
        tweets = source.harvested_tweets.exclude(created_at__isnull=True)
        chartGen.insertValues(tweets.extra({'date_created': "date(created_at)"}) \
                              .values('date_created') \
                              .annotate(date_count=Count('id')))
    return chartGen.generate()

def linechart_userPopularity(request):
    chartGen = LinechartGenerator()
    tableSelection = getUserSelection(request)
    selectedTWUsers = tableSelection.getSavedQueryset('TWUser', 'TWUserTable')
    for source in selectedTWUsers:
        chartGen.addColum({'label': '%s (Abonnés)' % (source.name if source.name else source.screen_name),
                           'type': 'number'})
        chartGen.insertValues(source.followers_counts.extra({'date_created': "date(recorded_time)",'date_count':'value'}) \
                              .values('date_created', 'date_count'))

    return chartGen.generate()

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

#####################  PIECHART  #############################
class PieChartGenerator:
    def __init__(self):
        self.table = {'cols': [{"id": "", "label": "Location", "pattern": "", "type": "string"},
                               {"id": "", "label": "Occurence", "pattern": "", "type": "number"}],
                      'rows': []}
        self.values = {}

    def put(self, key, val):
        if key in self.values:
            self.values[key] += val
        else:
            self.values[key] = val

    def generate(self, threshold):
        for key, val in reversed(sorted(self.values.items(), key=operator.itemgetter(1))):
            if val >= threshold:
                self.table['rows'].append({'c': [{'v': key}, {'v': val}]})
        return self.table

@login_required()
def pieChart(request):
    if 'ajax' in request.GET and request.GET['ajax'] == 'true': return ajax_pieChart(request)
    chart_type = request.GET['chart_type'] if 'chart_type' in request.GET else 'location'
    context = {
        'user': request.user,
        'chart_type': chart_type,
        'navigator': [
             ("Analytique","#"),
             ("Proportion", "#"),(chart_type,'#')
        ],
    }
    resetUserSelection(request)
    return render(request,'tool/pieChartTool.html', context)

def ajax_pieChart(request):
    reqId = None
    if 'tqx' in request.GET:
        reqId = request.GET['tqx'].split(':')[1]
    try:
        response = {
            "status": 'ok',
            'reqId': reqId,
            "table": generatepieChartTable(request),
        }
    except Exception as e:
        viewsLogger.exception('An error has occured while creating a PieChart')
        response = {
            'status': 'error',
            'reqId': reqId,
            'errors':[
                {
                    'reason':'internal_error',
                    'message': 'An error has occured while generating the data',
                    'detailed_message': str(e),
                }
            ],

        }
    return HttpResponse("google.visualization.Query.setResponse(%s)" % json.dumps(response),
                        content_type='application/json')

def generatepieChartTable(request):
    table = {}
    if request.GET['chart_type'] == 'location':
        table = piechart_location(request)
    else:
        raise Exception('Invalid chart_type value')
    if len(table['rows']) == 0:
        table = {'cols': [{"id": "", "label": "Location", "pattern": "", "type": "string"},
                 {"id": "", "label": "Occurence", "pattern": "", "type": "number"}],
                 'rows': [{'c': [{'v': 'Sélectionnez des éléments dans les tables ci-dessous (max 10)'}, {'v': 1}]}]}
    return table

def piechart_location(request):
    chartGen = PieChartGenerator()
    tableSelection = getUserSelection(request)
    twUserFollowerLoc = tableSelection.getSavedQueryset('TWUser', 'TWUserTableFollowerLoc')
    selectedTWHashHarvs = tableSelection.getSavedQueryset('HashtagHarvester', 'TWHashtagTable')

    if selectedTWHashHarvs.count() + twUserFollowerLoc.count() > 10:
        raise Exception('Please select at most 10 elements or create a group')

    followers = follower.objects.none()
    for source in twUserFollowerLoc:
        followers = followers | source.followers.filter(ended__isnull=True)
    locations = followers.distinct().values('value__location').annotate(c=Count('id'))
    for location in locations:
        if location['value__location']:
            cleanKey = location['value__location'].split(',')[0]
            cleanKey = cleanKey.title()
            chartGen.put(cleanKey, location['c'])

    tweets = Tweet.objects.none()
    for harv in selectedTWHashHarvs:
        tweets = tweets | harv.hashtag.tweets.filter(deleted_at__isnull=True)
    posters_locations = tweets.distinct().values('user__location').annotate(c=Count('id'))
    for location in posters_locations:
        if location['user__location']:
            cleanKey = location['user__location'].split(',')[0]
            cleanKey = cleanKey.title()
            chartGen.put(cleanKey, location['c'])

    threshold = 1
    if 'visibility_threshold' in request.GET: threshold = int(request.GET['visibility_threshold'])
    return chartGen.generate(threshold)


#####################  GEOCHART  #############################
@login_required()
def geoChart(request):
    context = {
        'user': request.user
    }
    return HttpResponse('geoChart', context)


#####################  BUBBLECHART  #############################
@login_required()
def bubbleChart(request):
    context = {
        'user': request.user
    }
    return HttpResponse('bubbleChart', context)


#####################  DISTRIBUTIONCHART  #############################
@login_required()
def distributionChart(request):
    context = {
        'user': request.user
    }
    return HttpResponse('distributionChart', context)


