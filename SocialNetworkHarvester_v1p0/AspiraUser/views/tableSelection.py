from django.contrib.auth.decorators import login_required
from AspiraUser.models import UserProfile, getUserSelection, resetUserSelection

from SocialNetworkHarvester_v1p0.jsonResponses import *
from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
from Twitter.models import *
from Youtube.models import *
from Facebook.models import *

log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0





@login_required()
def removeSelectedItems(request):
    aspiraErrors = []
    userProfile = request.user.userProfile
    selection = getUserSelection(request)
    queryset = selection.getSavedQueryset(None, request.GET['tableId'])
    successNum = 0
    listToRemovefrom = getattr(userProfile, request.GET['listToRemoveFrom'])
    for item in queryset:
        try:
            listToRemovefrom.remove(item)
            successNum += 1
        except:
            aspiraErrors.append('Something weird has happened while removing %s' % item)
    if aspiraErrors == []:
        response = {'status': 'ok', 'messages': [
            'Retiré %i élément%s de votre liste de collecte' % (successNum, 's' if successNum > 1 else '')]}
    else:
        response = {'status': 'exception', 'errors': aspiraErrors}
    selection.delete()
    return HttpResponse(json.dumps(response), content_type='application/json')

@login_required()
def addRemoveItemById(request, addRemove):
    if addRemove not in ['add', 'remove'] :return jsonBadRequest( "bad command: %s" %addRemove)
    for attr in ['id' ,'list']:
        if not attr in request.POST: return jsonBadRequest( "missing parameter: %s" %attr)
    id = request.POST['id']
    listName = request.POST['list']
    listLimit = listName+ 'Limit'

    user = request.user
    if not hasattr(user.userProfile, listName): return jsonBadRequest("no such list: %s" % listName)
    list = getattr(user.userProfile, listName)
    limit = getattr(user.userProfile, listLimit)
    model = list.model

    if not model.objects.filter(pk=id).exists(): return jsonBadRequest(
        'item #%s of type "%s" does not exists' % (id, model))
    item = model.objects.filter(pk=id).first()

    if addRemove == 'add':
        if item in list.all(): return jsonBadRequest("%s is already in current list" % item)
        if limit != 0 and list.count() >= limit:
            return jsonBadRequest("Vous avez atteint la limite pour cette liste de collecte. (%s éléments)" % limit)
        list.add(item)
        return jResponse(
                {'message': {"code": 200, "message": "<b>%s</b> as été ajouté de votre liste de collecte." % item}})
    else:
        if not item in list.all(): return jsonBadRequest("%s is not in current list" % item)
        list.remove(item)
        return jResponse(
                {'message': {"code": 200, "message": "<b>%s</b> as été retiré de votre liste de collecte." % item}})
