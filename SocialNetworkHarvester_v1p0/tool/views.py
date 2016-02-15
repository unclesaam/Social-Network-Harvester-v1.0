from django.shortcuts import *


# Create your views here.


def lineChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return render_to_response('tool/lineChartTool.html', context)


def pieChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('pieChart', context)


def geoChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('geoChart', context)


def bubbleChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('bubbleChart', context)


def distributionChart(request):
    context = RequestContext(request, {
        'user': request.user
    })
    return HttpResponse('distributionChart', context)
