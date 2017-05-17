from .commonThread import *


class FbCommentUpdater(CommonThread):
    batchSize = 5000
    workQueueName = 'commentUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbCommentList):
        client = getClient()
        response = client.get("",
                              ids=",".join([fbComment._ident for fbComment in fbCommentList]),
                              fields=['from','attachment','created_time','message_tags','message','object','parent',
                                      'comment_count','like_count']
                              )
        pretty(response)
        returnClient(client)

        '''
        for ident, item in response.items():
            if threadsExitFlag[0]: return
            fbPost = FBPost.objects.get(_ident=ident)
            self.setParentPost(fbPost, item)
            self.setAuthor(fbPost, item)
            self.setToProfile(fbPost, item)
            self.setTags(fbPost, item)
            fbPost.update(item)
            fbStatusList = [fbPost for fbPost in fbStatusList if fbPost._ident == ident]
        for fbPost in fbStatusList:
            log("%s was not retrievable from facebook"% fbPost)
            fbPost.error_on_update = True
            fbPost.save()
        '''

