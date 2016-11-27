from .commonThread import *

class TwUserUpdater(CommonThread):

    batchSize = 100
    workQueueName = 'updateQueue'

    #@twitterLogger.debug(showArgs=True)
    def method(self, userList):
        client = getClient('lookup_users')
        try:
            responses = client.call('lookup_users', user_ids=[user._ident for user in userList])
        except tweepy.error.TweepError:
            log('got tweepy.error.TweepError!')
            log('user_ids = %s'% [user._ident for user in userList])
            returnClient(client)
            raise
        returnClient(client)

        for response in responses:
            if threadsExitFlag[0]: return
            user = next((user for user in userList if user._ident == response._json['id']), None)
            if user:
                user.UpdateFromResponse(response._json)
                userList.remove(user)
        for user in userList:
            log('%s has returned no result. _error_on_update: %s'%(user,user._error_on_update))
            user._error_on_update = True
            user.save()
            log('_error_on_update: %s' % (user._error_on_update))