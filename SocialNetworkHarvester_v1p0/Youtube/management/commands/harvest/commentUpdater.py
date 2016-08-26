from .commonThread import *

class YTCommentUpdater(CommonThread):

    batchSize = 50

    #@youtubeLogger.debug()
    def execute(self):
        topCommentList = []
        repliesList = []
        while True:
            if threadsExitFlag[0]:
                break
            elif not commentToUpdateQueue.empty():
                comment = commentToUpdateQueue.get()
                if comment.parent_comment:
                    repliesList.append(comment)
                else:
                    topCommentList.append(comment)

                if len(repliesList) >= self.batchSize:
                    self.updateRepliesList(repliesList)
                    log("ytComments left to update: %s" % commentToUpdateQueue.qsize())
                    repliesList = []
                if len(topCommentList) >= self.batchSize:
                    self.updateTopCommentList(topCommentList)
                    log("ytComments left to update: %s" % commentToUpdateQueue.qsize())
                    topCommentList = []

            elif topCommentList or repliesList:
                if repliesList:
                    self.updateRepliesList(repliesList)
                    repliesList = []
                    log("ytComments left to update: %s" % commentToUpdateQueue.qsize())
                if topCommentList:
                    self.updateTopCommentList(topCommentList)
                    topCommentList = []
                    log("ytComments left to update: %s" % commentToUpdateQueue.qsize())

    #@youtubeLogger.debug(showArgs=True)
    def updateRepliesList(self, commentList):
        client = getClient()
        try:
            response = client.list(
                    'comments', id=",".join([comment._ident for comment in commentList]),
                    part='snippet,id'
            )
        except:
            returnClient(client)
            raise
        returnClient(client)

        for item in response['items']:
            if threadsExitFlag[0]:
                return
            comment = next((comment for comment in commentList if comment._ident == item['id']), None)
            if comment:
                comment.update(item)
                commentList.remove(comment)
                comment._last_updated = today()
                comment.save()
        for comment in commentList:
            log( '%s has returned no result' % comment)
            comment._deleted_at = today()
            comment.save()

    #@youtubeLogger.debug(showArgs=True)
    def updateTopCommentList(self,commentList):
        client = getClient()
        try:
            response = client.list('commentThreads', id=",".join([comment._ident for comment in commentList]),
                               part='snippet,id,replies')
        except:
            returnClient(client)
            raise
        returnClient(client)

        for item in response['items']:
            if threadsExitFlag[0]:
                return
            comment = next((comment for comment in commentList if comment._ident \
                            == item['snippet']['topLevelComment']['id']), None)
            if comment:
                comment.update(item['snippet']['topLevelComment'])
                commentList.remove(comment)
                comment._last_updated = today()
                comment.save()
                if 'replies' in item:
                    newReplies = 0
                    for jReply in item['replies']['comments']:
                        reply, new = YTComment.objects.get_or_create(_ident=jReply['id'])
                        if new:
                            reply.update(jReply)
                            newReplies += 1
                    if newReplies:
                        log('added %s replie%s to %s'%(
                            newReplies, plurial(newReplies),comment
                        ))
        for comment in commentList:
            log('%s has returned no result' % comment)
            comment._deleted_at = today()
            comment.save()