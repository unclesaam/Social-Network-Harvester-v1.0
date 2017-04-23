from .commonThread import *


class FbPageFeedHarvester(CommonThread):
    batchSize = 1
    workQueueName = 'pageFeedHarvestQueue'
    limit = 100
    itemIndex = 0

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbPageList):
        log("will harvest %s feed"%fbPageList[0])
        self.cursor = ClientItterator(fbPageList[0]._ident)
        self.updateCursor()
        item = self.getNext()
        while item:
            pretty(item)
            item = self.getNext()

    def updateCursor(self):
        self.cursor.kwargs = {"fields" : [{
            "feed.limit(%s)" % self.limit: [
                "created_time", "from", "parent_id", "status_type", "type",
                {"comments.limit(%s)" % self.limit: [
                    "created_time", "from", "parent",
                ]}
            ]}
        ]}

    def getNext(self):
        item = None
        try:
            item = self.cursor.next()
            self.itemIndex += 1
        except Exception as e:
            if e.args[0]["message"] == "Please reduce the amount of data you're asking for, then retry your request":
                self.limit = max(5, int(self.limit * 0.5))  # reducing the ammount of data asked for
                self.updateCursor()
                return self.getNext()
        if self.itemIndex >= self.limit:
            self.itemIndex = 0
            self.limit += 10 # augmenting the amount of data
        return item
