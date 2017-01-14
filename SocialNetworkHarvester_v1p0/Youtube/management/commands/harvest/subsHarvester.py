from .commonThread import *

class YTSubscriptionHarvester(CommonThread):

    batchSize = 1
    workQueueName = 'channelToSubsHarvestQueue'

    #@youtubeLogger.debug(showArgs=True)
    def method(self, channelList):
        channel = channelList[0]
        log('Will harvest %s\'s subscriptions'%channel)
        pageToken = None
        response = self.call(channel)
        actualSubs = []
        if not response or not response['items']:
            channel._last_subs_harvested = today()
            channel.save()
            log('Finished %s subs-harvest (0 subs added)' % (channel))
        while response and response['items']:
            for item in response['items']:
                channel, new = YTChannel.objects.get_or_create(_ident=item['snippet']['resourceId']['channelId'])
                actualSubs.append(channel)
                if new:
                    channelUpdateQueue.add(channel)
            if 'nextPageToken' in response:
                pageToken = response['nextPageToken']
                response = self.call(channel, pageToken)
            else:
                response = None

        self.createNewSubs(channel, actualSubs)
        self.filterOldSubs(channel, actualSubs)
        channel._last_subs_harvested = today()
        log('Finished %s\'s subs-harvest (%s comment%s added)' % (channel,
                                newCommentsNumber,plurial(newCommentsNumber)))
        channel.save()

    def call(self, channel, pageToken=None):
        response = None
        client = getClient()
        try:
            response = client.list('subscriptions', part='snippet',
                                   channelId=channel._ident, maxResults=50, pageToken=pageToken)
        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                log('%s has returned no results' % channel)
                channel._error_on_comment_harvest = True
                channel.save()
            elif hasattr(e, 'resp') and e.resp.status == 403:
                log('%s does not allow its subscriptions to be public' % channel)
                channel._public_subscriptions = False
                channel.save()
            else:
                returnClient(client)
                raise
        returnClient(client)
        return response

    def createNewSubs(self,channel,actualSubs):
        currentSubs = list(channel.Subscription.filter(ended__isnull=True).values('value'))
        for newSubChannel in list(set(actualSubs)-set(currentSubs)):
            newSub = Subscription.objects.create(channel=channel,value=newSubChannel)

    def filterOldSubs(self, channel, actualSubs):
        currentSubs = list(channel.Subscription.filter(ended__isnull=True).values('value'))
        for oldSubChannel in list(set(currentSubs) - set(actualSubs)):
            sub = Subscription.objects.get(channel=channel,value=oldSubChannel)
            sub.ended = today()
            sub.save()
