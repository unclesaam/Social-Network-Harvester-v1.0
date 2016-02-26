from .commonThread import *



class TwUserUpdater(CommonThread):

    userLookupBatchSize = 100

    @twitterLogger.debug()
    def execute(self):
        userWithIdsList = []
        userWithScreenNamesList = []
        log("twUsers left to update: %s"%updateQueue.qsize())
        while not threadsExitFlag[0]:
            #log('updaterExitFlag: %s'%updaterExitFlag[0])
            log("twUsers left to update: %s"%updateQueue.qsize())

            while len(userWithIdsList) < self.userLookupBatchSize \
                    and len(userWithScreenNamesList) < self.userLookupBatchSize:
                if threadsExitFlag[0]: return
#                updateQueueLock.acquire()
                if not updateQueue.empty():
                    twUser = updateQueue.get()
                    if hasattr(twUser, '_ident'):
                        userWithIdsList.append(twUser)
                    elif hasattr(twUser, 'screen_name'):
                        userWithScreenNamesList.append(twUser)
                #log('twuser: %s'%twUser)
#                updateQueueLock.release()

            if len(userWithIdsList) == self.userLookupBatchSize:
                self.updateTWuserList(userWithIdsList, 'user_ids')
                userWithIdsList = []
            elif len(userWithScreenNamesList) == self.userLookupBatchSize:
                self.updateTWuserList(userWithScreenNamesList, 'screen_names')
                userWithScreenNamesList = []

        if len(userWithIdsList) > 0:
            self.updateTWuserList(userWithIdsList, 'user_ids')
        elif len(userWithScreenNamesList) > 0:
            self.updateTWuserList(userWithScreenNamesList, 'screen_names')


    @twitterLogger.debug()
    def updateTWuserList(self, userList, callArg):
        client = getClient('lookup_users')
        if callArg =='screen_names':
            responses = client.call('lookup_users', screen_names=[user.screen_name for user in userList])
        elif callArg == 'user_ids':
            responses = client.call('lookup_users', user_ids=[user._ident for user in userList])
        else:
            raise Exception('Bad callArg: must be "screen_names" or "user_ids", got %s'%callArg)
        returnClient(client)


        for response in responses:
            if threadsExitFlag[0]: return
            if callArg =='screen_names':
                user = next((user for user in userList if user.screen_name == response._json['screen_name']), None)
            elif callArg == 'user_ids':
                user = next((user for user in userList if user._ident == response._json['id']), None)
            if user:
                user.UpdateFromResponse(response._json)
                userList.remove(user)
        for user in userList:
            log('%s has returned no result'%user)
            user._error_on_update = True
            user.save()