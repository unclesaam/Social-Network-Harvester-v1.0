from django.shortcuts import *
from django.http import StreamingHttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
import re, json
from SocialNetworkHarvester_v1p0.jsonResponses import *
import os

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG, STATIC_ROOT, STATICFILES_DIRS
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

@login_required
def downloadMedia(request):
    if not 'file' in request.GET: return jsonBadRequest(request, 'You must specify a filename')
    fileName = request.GET['file']
    if '..' in fileName: raise Http404()
    if DEBUG:
        filePath = os.path.join(STATICFILES_DIRS[0], 'medias/%s' % fileName)
    else:
        filePath = os.path.join(STATIC_ROOT, 'medias/%s'%fileName)
    if not os.path.exists(filePath): raise Http404()
    with open(filePath, 'rb') as pdf:
        response = HttpResponse(pdf.read(),content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=%s'%fileName
        return response
    pdf.closed

