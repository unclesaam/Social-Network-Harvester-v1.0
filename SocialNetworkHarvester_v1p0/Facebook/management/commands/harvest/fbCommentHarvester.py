from .commonThread import *


class FbCommentHarvester(CommonThread):
    batchSize = 1
    workQueueName = "commentHarvestQueue"
    queryLimit = 5000
    itemIndex = 0

    #@facebookLogger.debug(showArgs=True)
    def method(self, nodeList):
        node = nodeList[0]
        self.cursor = ClientItterator("%s/comments" % node._ident, limit=self.queryLimit)
        try:
            jObject = self.getNext()
        except ClientException as e:
            if re.match(r".*Object with ID '[0-9_]+' does not exist, cannot be loaded due to missing permissions, or does not support this operation\. .*", e.response['error']['message']):
                node.error_on_harvest = True
                node.save()
                log("could not harvest comments from %s"%node)
                return
            else: raise
        while jObject:
            if threadsExitFlag[0]: return
            fbProfile, new = FBProfile.objects.get_or_create(_ident=jObject['from']['id'])
            if new:
                profileUpdateQueue.put(fbProfile)
            fbComment, new = FBComment.objects.get_or_create(_ident=jObject['id'])
            if new:
                fbComment.parentPost = node
                fbComment.from_profile = fbProfile
                fbComment.save()
                commentUpdateQueue.put(fbComment)
                reactionHarvestQueue.put(fbComment)
            jObject = self.getNext()
        node.last_comments_harvested = today()
        node.save()

    def updateCursor(self):
        self.cursor.kwargs['limit'] = self.queryLimit
        log("queryLimit: %s"%self.queryLimit)

    def getNext(self):
        try:
            item = self.cursor.next()
            self.itemIndex += 1
            if self.itemIndex >= self.queryLimit:
                self.itemIndex = 0
                self.queryLimit = min(self.queryLimit+5, 5000)  # augmenting the amount of requested data (max 5000)
                self.updateCursor()
        except ClientException as e:
            if e.response["error"]["message"] in \
                    ["Please reduce the amount of data you're asking for, then retry your request",
                     "An unknown error occurred"]:
                self.queryLimit = max(5, int(self.queryLimit * 0.5))  # reducing the ammount of requested data
                self.updateCursor()
                return self.getNext()
            else: raise
        return item
