from django.contrib.auth.decorators import login_required
from Twitter.models import *
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from SocialNetworkHarvester_v1p0.jsonResponses import *
from AspiraUser.models import getUserSelection, resetUserSelection
import re
from tool.views.ajaxTables import readLinesFromCSV
import tweepy

import re

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0
logerror = lambda s: viewsLogger.exception(s) if DEBUG else 0


@login_required()
def addUser(request):
    occuredErrors = []
    userProfile = request.user.userProfile
    try:
        api = getTwitterApi(userProfile)
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'exception', 'errors': str(e)}), content_type='application/json')
    screen_names = [sn for sn in request.POST.getlist('screen_name') if sn != '']
    if 'Browse' in request.FILES:
        sns, errors = readScreenNamesFromCSV(request.FILES['Browse'])
        screen_names += sns
        for error in errors:
            occuredErrors.append('Une erreur est survenue lors de la lecture de votre fichier csv. à la ligne %i.'%error)

    if not screen_names:
        occuredErrors.append("Écrivez au moins un nom d'utilisateur.")

    added_screen_names = []
    for screen_name_list in [screen_names[x:x+100] for x in range(0,len(screen_names),100)]:
        if userProfile.twitterUsersToHarvest.count() >= userProfile.twitterUsersToHarvestLimit:
            occuredErrors.append(
                'Vous avez atteint la limite d\'utilisateurs Twitter pour ce compte! (limite: %i)'%
                userProfile.twitterUsersToHarvestLimit
            )
            break
        try:
            response = api.lookup_users(screen_names=screen_name_list)
            for item in response:
                if userProfile.twitterUsersToHarvest.count() >= userProfile.twitterUsersToHarvestLimit:
                    break
                twUser, new = TWUser.objects.get_or_create(_ident=item.id)
                if new:
                    twUser.UpdateFromResponse(item._json)
                twUser._update_frequency = 1
                twUser.save()
                userProfile.twitterUsersToHarvest.add(twUser)
                added_screen_names.append(twUser.screen_name)
        except tweepy.error.TweepError as e:
            if e.api_code == 17:
                pass
            else:
                raise

    if occuredErrors:
        response = {'status': 'exception', 'errors': occuredErrors}
    else:
        introuvables = [screen_name for screen_name in screen_names if screen_name not in added_screen_names]
        response = {'status': 'ok', 'messages':
            '%i L\'utilisateur Twitter %s a été ajouté à votre liste.' % (
            len(added_screen_names), 's' if len(added_screen_names) > 1 else '')
        }
        if introuvables:
            response['errors']=["Le nom d'utilisateur <b>%s</b> est introuvable ou l'utilisateur préfère " \
                                "garder ses informations privées."%introuvable for introuvable in introuvables]
    return HttpResponse(json.dumps(response), content_type='application/json')


def getTwitterApi(userProfile):
    if not all([
        userProfile.twitterApp_access_token_key,
        userProfile.twitterApp_access_token_secret,
        userProfile.twitterApp_consumerKey,
        userProfile.twitterApp_consumer_secret
    ]):
        raise Exception(
            "Vous devez d'abord configurer votre application Twitter! Veuillez visiter votre page de "
            "<a href='/user/settings' class='TableToolLink'>paramètres</a> et suivre la procédure décrite dans "
            "la section \"Twitter\"."
        )
    try:
        auth = tweepy.OAuthHandler(userProfile.twitterApp_consumerKey, userProfile.twitterApp_consumer_secret)
        auth.set_access_token(userProfile.twitterApp_access_token_key, userProfile.twitterApp_access_token_secret)
        api = tweepy.API(auth)
        api.me()
        return api
    except tweepy.error.TweepError as e:
        if e.api_code == 32:
            userProfile.twitterApp_parameters_error = True
            userProfile.save()
            logerror('Error in Twitter.forms.py: addUser')
            raise Exception(
                "Un problème est survenu avec votre application Twitter! Veuillez visiter votre page de "
                "<a href='/user/settings' class='TableToolLink'>paramètres</a> et assurez-vous que les informations "
                "inscrites dans la section \"Twitter\" sont correctes."
            )
        else:
            raise

#@viewsLogger.debug(showArgs=True)
def readScreenNamesFromCSV(file):
    screen_names = []
    errors = []
    rowNum = 0
    for row in file:
        rowNum += 1
        try:
            decodedRow = row.decode('utf8')
            decodedRow = re.sub('[\\r\\n]', '', decodedRow)
            screen_names.append(decodedRow)
        except UnicodeDecodeError:
            #log('an invalid line was retrieved')
            errors.append(rowNum)
    return screen_names, errors

def screenNameIsValid(screen_name):
    if re.match('^[a-zA-z0-9_]+$', screen_name):
        return True
    return False


@login_required()
def addHashtag(request):
    aspiraErrors = []
    userProfile = request.user.userProfile
    terms = request.POST.getlist('hashtags')
    starts = request.POST.getlist('starts')
    ends = request.POST.getlist('ends')
    hashtags = [(terms[i],starts[i],ends[i]) for i in range(0,len(terms)) if terms[i] != '']
    success_count = 0

    if 'Browse' in request.FILES:
        hs, errors = readHashtagsFromCSV(request.FILES['Browse'])
        hashtags += hs
        for error in errors:
            aspiraErrors.append('Une erreur est survenue lors de la lecture de votre fichier, sur la ligne %i.' % error)

    log(hashtags)
    for hashtag in hashtags:
        term = re.sub('(,+$)|#', '', hashtag[0])
        try:
            start = datetime.strptime(hashtag[1], '%m/%d/%Y')
        except ValueError:
            aspiraErrors.append('La date de départ ("%s") n\'est pas valide'% hashtag[1])
            continue
        try:
            end = datetime.strptime(hashtag[2], '%m/%d/%Y')
        except ValueError:
            aspiraErrors.append('La date de fin ("%s") n\'est pas valide' % hashtag[2])
            continue
        if hashtagIsValid(term, start, end):
            twHashtag, new = Hashtag.objects.get_or_create(term=term)
            harvester, new = HashtagHarvester.objects.get_or_create(hashtag=twHashtag, _harvest_since=start,_harvest_until=end)
            if userProfile.twitterHashtagsToHarvest.count() < userProfile.twitterHashtagsToHarvestLimit:
                if not userProfile.twitterHashtagsToHarvest.filter(pk=harvester.pk).exists():
                    userProfile.twitterHashtagsToHarvest.add(harvester)
                    success_count += 1
            else:
                aspiraErrors.append(
                    'Vous avez atteint la limite de hastags à aspirer pour ce compte! (limite: %i)' %
                    userProfile.twitterHashtagsToHarvestLimit
                )
                break
        else:
            aspiraErrors.append('Le format du hastag (%s) n\'est pas valide.' % str(hashtag))

    if aspiraErrors:
        response = {'status':'exception','errors' : aspiraErrors}
    else:
        response = {'status': 'ok', 'messages': ['%i nouveaux Hashtag%s %s été ajouté%s à votre liste.' % (
            success_count, 's' if success_count > 1 else '', 'ont' if success_count > 1 else 'a',
            's' if success_count > 1 else '')]}

    return HttpResponse(json.dumps(response), content_type='application/json')


def hashtagIsValid(term, start, end):
    log('hashtag: %s, %s-%s'%(term, start, end))
    valid = True
    if not re.match('^#?[a-zA-z0-9_]+$', term):
        valid = False
    if start >= end:
        valid = False
    log('%s'%('valid' if valid else 'invalid'))
    return valid


def readHashtagsFromCSV(file):
    hashtags = []
    errors = []
    rowNum = 0
    for row in file:
        rowNum += 1
        try:
            decodedRow = row.decode('utf8')
            decodedRow = re.sub('[\\r\\n]', '', decodedRow)
            decodedRow = re.sub(',+$', '', decodedRow)
            log(decodedRow)
            if decodedRow != '':
                (term, start, end) = decodedRow.split(',')
                hashtags.append((term, start, end))
        except:
            errors.append(rowNum)
    return hashtags, errors