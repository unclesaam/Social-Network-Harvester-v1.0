from .commonThread import *

class TwUserUpdater(CommonThread):

    batchSize = 100
    workQueueName = 'updateQueue'

    #@twitterLogger.debug(showArgs=True)
    def method(self, userList):
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