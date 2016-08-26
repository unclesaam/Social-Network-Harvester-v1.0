from .commonThread import *

class YTCommentHarvester(CommonThread):

    batchSize = 1

    #@youtubeLogger.debug()
    def execute(self):
        channelList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not channelsToCommentHarvestQueue.empty():
                channel = channelsToCommentHarvestQueue.get()
                channelList.append(channel)
                if len(channelList) >= self.batchSize:
                    self.harvestChannelList(channelList)
                    log("ytChannels left to comment-harvest: %s" % channelsToCommentHarvestQueue.qsize())
                    channelList = []
            elif len(channelList) > 0:
                self.harvestChannelList(channelList)
                log("ytChannels left to comment-harvest: %s" % channelsToCommentHarvestQueue.qsize())
                channelList = []

    #@youtubeLogger.debug(showArgs=True)
    def harvestChannelList(self, channelList):
        channel = channelList[0]
        log('Will harvest %s\'s channel and video comments'%channel)
        newCommentsNumber = 0
        harvestOverlap = 0
        pageToken = None
        if not channel._has_reached_comments_begining:
            pageToken =  channel._earliest_comment_page_token
        response = self.call(channel, pageToken)
        if not response or not response['items']:
            channel._last_comment_harvested = today()
            channel.save()
            log('Finished %s comment-harvest (0 comment added)' % (channel))
        while response and response['items']:
            for item in response['items']:
                comment, new = YTComment.objects.get_or_create(_ident=item['snippet']['topLevelComment']['id'])
                if new:
                    harvestOverlap = 0
                    newCommentsNumber += 1
                else:
                    harvestOverlap += 1
                    if channel._has_reached_comments_begining and harvestOverlap > 100:
                        channel._last_comment_harvested = today()
                        channel.save()
                        log('Finished %s comment-harvest (%s comment%s added)'%(channel,
                                                        newCommentsNumber, plurial(newCommentsNumber)))
                        return
                comment.update(item['snippet']['topLevelComment'])
                if 'replies' in item:
                    for jReply in item['replies']['comments']:
                        reply, new = YTComment.objects.get_or_create(_ident=jReply['id'])
                        if new:
                            reply.update(jReply)

            if 'nextPageToken' in response:
                channel._earliest_comment_page_token = response['nextPageToken']
                pageToken = response['nextPageToken']
                response = self.call(channel, pageToken)

            else:
                response = None
                channel._has_reached_comments_begining = True
                channel._last_comment_harvested = today()
                log('Finished %s\'s comment-harvest (%s comment%s added)' % (channel,
                                        newCommentsNumber,plurial(newCommentsNumber)))
            channel.save()





    def call(self, channel, pageToken):
        response = None
        client = getClient()
        try:
            response = client.list('commentThreads', allThreadsRelatedToChannelId=channel._ident,
                                   part='snippet,replies', maxResults=100, pageToken=pageToken)
        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                log('%s has returned no results' % channel)
                channel._error_on_comment_harvest = True
                channel.save()
            else:
                returnClient(client)
                raise
        returnClient(client)
        return response