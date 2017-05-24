from .commonThread import *


class FBProfileUpdater(CommonThread):
    batchSize = 50
    workQueueName = 'profileUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbProfileList):

        client = getClient()
        response = client.get("",
                              ids=",".join([fbProfile._ident for fbProfile in fbProfileList]),
                              metadata='true',
                              fields=[{'metadata':['type']}]
                              )
        #pretty(response)
        returnClient(client)

        for ident, item in response.items():
            if threadsExitFlag[0]: return
            fbProfile = FBProfile.objects.get(_ident=ident)
            fbProfile.update(item)
        for fbProfile in fbProfileList:
            if fbProfile._ident not in response.keys():
                log("%s was not retrievable from facebook"% fbProfile)
                fbProfile.deleted_at = today()
                fbProfile.save()

