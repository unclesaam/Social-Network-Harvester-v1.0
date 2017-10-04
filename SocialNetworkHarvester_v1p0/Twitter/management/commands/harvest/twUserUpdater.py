from .commonThread import *

class TwUserUpdater(CommonThread):

    batchSize = 100
    workQueueName = 'updateQueue'

    #@twitterLogger.debug(showArgs=True)
    def method(self, twUserList):
        client = getClient('lookup_users')
        try:
            responses = client.call('lookup_users', user_ids=[user._ident for user in twUserList])
        except tweepy.error.TweepError:
            log('got tweepy.error.TweepError!')
            log('user_ids = %s' % [user._ident for user in twUserList])
            returnClient(client)
            raise
        returnClient(client)

        for response in responses:
            if threadsExitFlag[0]: return
            twUser = next((user for user in twUserList if user._ident == response._json['id']), None)
            if twUser:
                if twUser.harvested_by.count():
                    twUser._update_frequency = 1
                else:
                    twUser._update_frequency = 5
                twUser.save()
                twUser.UpdateFromResponse(response._json)
                twUserList.remove(twUser)
        for twUser in twUserList:
            log('(%s) has returned no result.'%twUser)
            #twUser._error_on_update = True
            twUser._last_updated = today()
            twUser._update_frequency = 5
            twUser.save()