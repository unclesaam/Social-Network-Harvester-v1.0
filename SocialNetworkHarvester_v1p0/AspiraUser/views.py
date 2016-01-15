from django.shortcuts import *

def userDashboard(request):
	return render_to_response('AspiraUser/dashboard.html')