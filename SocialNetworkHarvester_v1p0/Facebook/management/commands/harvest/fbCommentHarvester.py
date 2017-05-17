from .commonThread import *


class FbCommentHarvester(CommonThread):
    batchSize = 1
    workQueueName = "commentHarvestQueue"
    queryLimit = 5000

    #@facebookLogger.debug(showArgs=True)
    def method(self, nodeList):
        node = nodeList[0]
        cursor = ClientItterator("%s/comments" % node._ident, limit=self.queryLimit)
        jObject = cursor.next()
        while jObject:
            if threadsExitFlag[0]: return
            fbProfile, new = FBProfile.objects.get_or_create(_ident=jObject['from']['id'])
            if new: profileUpdateQueue.put(fbProfile)
            fbComment, new = FBComment.objects.get_or_create(_ident=jObject['id'])
            if new:
                fbComment.parentPost = node
                fbComment.from_profile = fbProfile
                fbComment.save()
                commentUpdateQueue.put(fbComment)
            jObject = cursor.next()
        node.last_comments_harvested = today()
        node.save()

