from django.shortcuts import *
from django.contrib.auth.decorators import login_required


@login_required()
def selectBase(request):
    return HttpResponse("selectBase")