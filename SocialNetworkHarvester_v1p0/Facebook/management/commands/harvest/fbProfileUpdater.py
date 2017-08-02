from .commonThread import *


class FBProfileUpdater(CommonThread):
    batchSize = 50
    workQueueName = 'profileUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbProfileList):

        client = getClient()
        try:
            response = client.get("",
                              ids=",".join([fbProfile._ident for fbProfile in fbProfileList]),
                              metadata='true',
                              fields=[{'metadata':['type']}])
        except ClientException as e:
            if e.response['error']['code'] == 21:
                returnClient(client)
                #logerror(e)
                match = re.search(r".*Page ID (?P<id1>[0-9]+) was migrated to page ID (?P<id2>[0-9]+).*",
                                  e.response['error']['message'])
                if match:
                    fbProfile = FBProfile.objects.get(_ident=match.group('id1'))
                    fbProfile.migrateId(match.group('id2'))
                    log('FBProfile "%s" was migrated to new ID (%s)'%(self, match.group('id2')))
                    return
                else: raise e

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