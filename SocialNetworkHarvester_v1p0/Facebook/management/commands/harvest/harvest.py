
from AspiraUser.models import UserProfile
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_admins, EmailMessage
from django.contrib.auth.models import User
from .fbPageUpdater import *
from .fbPageFeedHarvester import *
from .fbStatusUpdater import *
from .fbReactionHarvester import *
from .fbCommentHarvester import *
from .fbCommentUpdater import *
from .fbProfileUpdater import *
from django.core.paginator import Paginator
import io, csv, types

myEmailMessage = ["Facebook harvest routine has completed successfully"]
myEmailTitle = ["Facebook harvest completed"]
threadList = [[]]

RAMUSAGELIMIT = 600000000 # in bytes
GRAPHRAMUSAGE = False

@facebookLogger.debug()
def harvestFacebook():

    #Comment these lines in production
    # resetFacebookAppError()
    # resetLastUpdated()
    # resetLastHarvested()

    all_profiles = UserProfile.objects.filter(facebookApp_parameters_error=False)
    clientList = getClientList(all_profiles)
    all_profiles = all_profiles.filter(facebookApp_parameters_error=False)
    log('facebookApp_parameters_error profiles: %s'% UserProfile.objects.filter(facebookApp_parameters_error=True))
    if len(all_profiles) == 0 :
        log('No valid Facebook client exists!')
        myEmailTitle[0] = 'Facebook has not launched'
        myEmailMessage[0] = 'No valid Facebook client exists! (reseting them all)'
        for profile in UserProfile.objects.all():
            profile.facebookApp_parameters_error = False
            profile.save()
        return
    clientQueue.maxsize = len(clientList)
    log("clients: %s" % [client.name for client in clientList])
    for client in clientList:
        clientQueue.put(client)


    for thread in [
      (launchFbPagesUpdateThreads, 'launchPagesUpdate', {'profiles': all_profiles}),
      (launchFbPageFeedHarvestThreads, 'launchFbPageFeedHarvest', {'profiles': all_profiles}),
        (launchFbStatusUpdateThreads, 'launchFbPostUpdateThreads', {'profiles': all_profiles}),
        # (launchFbReactionHarvestThreads, 'launchFbReactionHarvestThreads', {'profiles': all_profiles}),
       # (launchFbCommentHarvestThreads, 'launchFbCommentHarvestThreads', {'profiles': all_profiles}),
           # (launchFBCommentUpdateThreads, 'launchFBCommentUpdateThreads', {'profiles': all_profiles}),
         (launchFBProfileUpdateThreads, 'launchFBProfileUpdateThreads', {}),
        #TODO: Update FBUsers, fbGroups, fbEvents, fbApplications, fbVideos
    ]:
        t = threading.Thread(target=thread[0],name=thread[1],kwargs=thread[2])
        threadList[0].append(t)
        t.start()

    time.sleep(20) # gives some time to the feeder-threads to initialize
    waitForThreadsToEnd()



############# THREADS LAUNCHERS ##############


def launchFbPagesUpdateThreads(*args, **kwargs):
    priorityUpdates = orderQueryset(FBPage.objects.filter(harvested_by__isnull=False, error_on_update=False)
                                    .distinct(), 'last_updated', delay=0.5)
    allPagesToUpdate = orderQueryset(FBPage.objects.filter(error_on_update=False)
                                     .exclude(pk__in=priorityUpdates), 'last_updated', delay=5)
    threadNames = ['pageUpdater',]
    for threadName in threadNames:
        thread = FbPageUpdater(threadName)
        thread.start()
        threadList[0].append(thread)

    put_batch_in_queue(pageUpdateQueue, priorityUpdates)
    put_batch_in_queue(pageUpdateQueue, allPagesToUpdate)

def launchFbPageFeedHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    pagesToFeedHarvest = FBPage.objects.none()
    for profile in profiles:
        pagesToFeedHarvest = pagesToFeedHarvest | profile.facebookPagesToHarvest.filter(error_on_harvest=False)

    pagesToFeedHarvest = orderQueryset(pagesToFeedHarvest.distinct(), 'last_feed_harvested', delay=1)

    threadNames = ['pagefee_harv_1', ]#'pagefee_harv_2']
    for threadName in threadNames:
        thread = FbPageFeedHarvester(threadName)
        thread.start()
        threadList[0].append(thread)

    put_batch_in_queue(pageFeedHarvestQueue, pagesToFeedHarvest)

def launchFbStatusUpdateThreads(*args, **kwargs):
    fbPostsToUpdate = orderQueryset(FBPost.objects.filter(error_on_update=False), 'last_updated', delay=2)
    threadNames = ['status_updt_1']
    for threadName in threadNames:
        thread = FbStatusUpdater(threadName)
        thread.start()
        threadList[0].append(thread)

    put_batch_in_queue(statusUpdateQueue, fbPostsToUpdate)

def launchFBCommentUpdateThreads(*args, **kwargs):
    fbCommentsToUpdate = orderQueryset(FBComment.objects.filter(error_on_update=False), 'last_updated', delay=4)
    threadNames = ['cmt_updt_1']
    for threadName in threadNames:
        thread = FbCommentUpdater(threadName)
        thread.start()
        threadList[0].append(thread)

    put_batch_in_queue(commentUpdateQueue, fbCommentsToUpdate)

def launchFbReactionHarvestThreads(*args, **kwargs):
    fbPostsToReactHarvest = orderQueryset(
            FBPost.objects.filter(error_on_harvest=False), 'last_reaction_harvested', delay=5)
    fbCommentsToReactHarvest = orderQueryset(
            FBComment.objects.filter(error_on_harvest=False), 'last_reaction_harvested', delay=5)
    threadNames = ['react_harv_1','react_harv_2']
    for threadName in threadNames:
        thread = FbReactionHarvester(threadName)
        thread.start()
        threadList[0].append(thread)

    put_batch_in_queue(reactionHarvestQueue, fbPostsToReactHarvest)
    put_batch_in_queue(reactionHarvestQueue, fbCommentsToReactHarvest)

def launchFbCommentHarvestThreads(*args, **kwargs):
    profiles = kwargs['profiles']
    fbPostsToCommentHarvest = FBPost.objects.none()
    for profile in profiles:
        for fbPage in profile.facebookPagesToHarvest.all():
            fbPostsToCommentHarvest = fbPostsToCommentHarvest | fbPage.fbProfile.postedStatuses.filter(error_on_harvest=False)
    fbPostsToCommentHarvest = orderQueryset(fbPostsToCommentHarvest, 'last_comments_harvested', delay=2)
    threadNames = ['commt_harv_1']
    for threadName in threadNames:
        thread = FbCommentHarvester(threadName)
        thread.start()
        threadList[0].append(thread)
    put_batch_in_queue(commentHarvestQueue, fbPostsToCommentHarvest)

def launchFBProfileUpdateThreads(*args, **kwargs):
    threadNames = ['profileUpdater1']
    for threadName in threadNames:
        thread = FBProfileUpdater(threadName)
        thread.start()
        threadList[0].append(thread)
    put_batch_in_queue(profileUpdateQueue, FBProfile.objects.filter(deleted_at__isnull=True).filter(type=""))

################# UTILS ####################

def getClientList(profiles):
    clientList = []
    for profile in profiles:
        if not hasattr(profile,'fbAccessToken'):
            profile.facebookApp_parameters_error = True
            profile.save()
        else:
            client = createClient(profile)
            if client:
                try:
                    me = client.get('me')
                    clientList.append(client)
                except Exception as e:
                    log("An error was recovered while validating %s's facebook access token:"%profile)
                    logerror(e)
                    profile.facebookApp_parameters_error = True
                    profile.save()
    return clientList

def orderQueryset(queryset, dateTimeFieldName,delay=1):
    isNull = dateTimeFieldName+"__isnull"
    lt = dateTimeFieldName+"__lt"
    ordered_elements = queryset.filter(**{isNull:True}) | \
                       queryset.filter(**{lt: xDaysAgo(delay)}).order_by(dateTimeFieldName)
    return ordered_elements

def put_batch_in_queue(queue, queryset):
    paginator = Paginator(queryset, 1000)
    for page in range(1, paginator.num_pages + 1):
        for item in paginator.page(page).object_list:
            if threadsExitFlag[0]: return
            if QUEUEMAXSIZE == 0 or queue.qsize() < QUEUEMAXSIZE:
                queue.put(item)
            else:
                time.sleep(1)

def resetFacebookAppError():
    for profile in UserProfile.objects.filter(facebookApp_parameters_error=True):
        profile.facebookApp_parameters_error = False
        profile.save()

def resetLastUpdated():
    for page in FBPage.objects.filter(last_updated__isnull=False):
        page.last_updated = None
        page.save()
    for post in FBPost.objects.filter(last_updated__isnull=False):
        post.last_updated = None
        post.save()
    for comment in FBComment.objects.filter(last_updated__isnull=False):
        comment.last_updated = None
        comment.save()

def resetLastHarvested():
    for page in FBPage.objects.filter(last_feed_harvested__isnull=False):
        page.last_feed_harvested = None
        page.save()
    for post in FBPost.objects.filter(last_comments_harvested__isnull=False):
        post.last_comments_harvested = None
        post.save()
    for post in FBPost.objects.filter(last_reaction_harvested__isnull=False):
        post.last_reaction_harvested = None
        post.save()

def send_routine_email(title,message):
    logfilepath = os.path.join(LOG_DIRECTORY, 'facebook.log')
    logfile = open(logfilepath, 'r')
    adresses = [user.email for user in User.objects.filter(is_superuser=True)]
    try:
        email = EmailMessage(title, message)
        email.attachments = [('facebookLogger.log', logfile.read(), 'text/plain')]
        email.to = adresses
        email.from_email = 'Aspira'
        email.send()
        print('%s - Routine email sent to %s'%(datetime.now().strftime('%y-%m-%d_%H:%M'),adresses))
    except Exception as e:
        print('Routine email failed to send')
        print(e)
        facebookLogger.exception('An error occured while sending an email to admin')

@facebookLogger.debug()
def waitForThreadsToEnd():
    notEmptyQueuesNum = -1
    t = time.time()
    while notEmptyQueuesNum != 0 and exceptionQueue.empty():
        time.sleep(3)
        if process.memory_info()[0] >= RAMUSAGELIMIT:
            log('MEMORY USAGE LIMIT EXCEDED!')
            myEmailTitle[0] = 'MEMORY USAGE LIMIT EXCEDED!'
            myEmailMessage[0] = 'Python script memory usage has exceded the set limit (%s Mb)'% \
                                (RAMUSAGELIMIT/1000000)
            return stopAllThreads()
        notEmptyQueues = [(queue._name, queue.qsize()) for queue in allQueues if not queue.empty()]
        if len(notEmptyQueues) != notEmptyQueuesNum and len(notEmptyQueues) <= 20 or \
                t + 60 < time.time(): # each minute
            log('Working Queues: %s' % notEmptyQueues)
            notEmptyQueuesNum = len(notEmptyQueues)
            t = time.time()
    return stopAllThreads()

@facebookLogger.debug()
def stopAllThreads():
    time.sleep(3)
    threadsExitFlag[0] = True
    t = time.time()
    aliveThreads = [thread.name for thread in threadList[0] if thread.isAlive()]
    while len(aliveThreads) > 0 or not exceptionQueue.empty():
        if t + 10 < time.time():
            t = time.time()
            lastAliveThreads = aliveThreads
            aliveThreads = [thread.name for thread in threadList[0] if thread.isAlive()]
            if aliveThreads != lastAliveThreads:
                log('Alive Threads: %s' % aliveThreads)
        if not exceptionQueue.empty():
            (e, threadName) = exceptionQueue.get()
            try:
                raise e
            except:
                myEmailMessage[0] = 'An exception has been retrieved from a Thread. (%s)' % threadName
                myEmailTitle[0] = 'SNH - Facebook harvest routine error'
                logerror(myEmailMessage[0])