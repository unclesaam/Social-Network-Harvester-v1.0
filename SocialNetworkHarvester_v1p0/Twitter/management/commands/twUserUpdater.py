from .commonThread import *



class TwUserUpdater(CommonThread):

    userLookupBatchSize = 100

    #@twitterLogger.debug()
    def execute(self):
        userList = []
        #log("twUsers left to update: %s"%updateQueue.qsize())
        while not threadsExitFlag[0]:
            #log('updaterExitFlag: %s'%updaterExitFlag[0])
            log("twUsers left to update: %s"%updateQueue.qsize())
            while len(userList) < self.userLookupBatchSize:
                if threadsExitFlag[0]:
                    break
                else:
                    twUser = updateQueue.get()
                    userList.append(twUser)
            if len(userList) == self.userLookupBatchSize:
                self.updateTWuserList(userList)
                userList = []
        if len(userList) > 0:
            self.updateTWuserList(userList)


    #@twitterLogger.debug(showArgs=True)
    def updateTWuserList(self, userList):
        client = getClient('lookup_users')
        responses = client.call('lookup_users', user_ids=[user._ident for user in userList])
        returnClient(client)

        for response in responses:
            if threadsExitFlag[0]: return
            user = next((user for user in userList if user._ident == response._json['id']), None)
            if user:
                user.UpdateFromResponse(response._json)
                userList.remove(user)
        for user in userList:
            log('%s has returned no result'%user)
            user._error_on_update = True
            user.save()