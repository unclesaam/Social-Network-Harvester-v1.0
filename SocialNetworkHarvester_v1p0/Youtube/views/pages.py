from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from AspiraUser.views import addMessagesToContext
from AspiraUser.models import getUserSelection, resetUserSelection


@login_required()
def youtubeBase(request):
	context = RequestContext(request, {
		'user': request.user,
		"navigator": [
			("Youtube", "/youtube"),
		]
	})
	request, context = addMessagesToContext(request, context)
	resetUserSelection(request)
	return render_to_response('Youtube/YoutubeBase.html', context)