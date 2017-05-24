from .commonThread import *


class FbCommentUpdater(CommonThread):
    batchSize = 50
    workQueueName = 'commentUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbCommentList):
        client = getClient()
        response = client.get("",
                              ids=",".join([fbComment._ident for fbComment in fbCommentList]),
                              fields=['from','attachment','created_time','message_tags','message','object','parent',
                                      'comment_count','like_count','permalink_url']
                              )
        #pretty(response)
        returnClient(client)

        for ident, item in response.items():
            if threadsExitFlag[0]: return
            fbComment = FBComment.objects.get(_ident=ident)
            fbComment.update(item)
        for fbComment in fbCommentList:
            if fbComment._ident not in response.keys():
                log("%s was not retrievable from facebook"% fbComment)
                fbComment.error_on_update = True
                fbComment.save()
