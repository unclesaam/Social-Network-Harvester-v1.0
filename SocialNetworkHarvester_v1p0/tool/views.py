from django.shortcuts import *

# Create your views here.


def lineChart(request):
	return render_to_response('tool/lineChartTool.html')

def pieChart(request):
	return HttpResponse('pieChart')

def geoChart(request):
	return HttpResponse('geoChart')

def bubbleChart(request):
	return HttpResponse('bubbleChart')

def distributionChart(request):
	return HttpResponse('distributionChart')
