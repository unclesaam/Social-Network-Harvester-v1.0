from .commonThread import *


class FbPageFeedHarvester(CommonThread):
    batchSize = 1
    workQueueName = 'pageFeedHarvestQueue'
    limit = 100
    itemIndex = 0

    #@facebookLogger.debug(showArgs=True, showClass=True)
    def method(self, fbPageList):
        log("will harvest %s feed"%fbPageList[0])
        self.cursor = ClientItterator("%s/feed"%fbPageList[0]._ident, limit=self.limit,
                                      fields=["created_time", "from", "parent_id", "status_type", "type"])
        self.updateCursor()
        item = self.getNext()
        while item:
            if threadsExitFlag[0]: return
            fbPost, new = FBPost.objects.get_or_create(_ident=item['id'])
            if new:
                fbPost.from_profile, new = FBProfile.objects.get_or_create(_ident=item['from']["id"])
                fbPost.from_profile.findAndSetInstance()
                if "parent_id" in item:
                    fbPost.parent_post, new = FBPost.objects.get_or_create(_ident=item['parent_id'])
                if "status_type" in item:
                    fbPost.status_type = item['status_type']
                if "type" in item:
                    fbPost.type = item['type']
                fbPost.created_time = item['created_time']
                fbPost.save()
                statusUpdateQueue.put(fbPost)
            item = self.getNext()
        fbPageList[0].last_feed_harvested = today()
        fbPageList[0].save()


    #@facebookLogger.debug(showArgs=True, showClass=True)
    def updateCursor(self):
        self.cursor.kwargs['limit'] = self.limit

    #@facebookLogger.debug(showArgs=True, showClass=True)
    def getNext(self):
        try:
            item = self.cursor.next()
            self.itemIndex += 1
            if self.itemIndex >= self.limit:
                self.itemIndex = 0
                self.limit = min(self.limit+5, 100)  # augmenting the amount of requested data (max 100)
                self.updateCursor()
        except Exception as e:
            if e.args[0]["message"] == "Please reduce the amount of data you're asking for, then retry your request":
                self.limit = max(5, int(self.limit * 0.5))  # reducing the ammount of requested data
                self.updateCursor()
                return self.getNext()
            else: raise
        return item
