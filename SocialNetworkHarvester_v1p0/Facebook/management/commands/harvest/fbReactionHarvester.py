from .commonThread import *


class FbReactionHarvester(CommonThread):
    batchSize = 1
    workQueueName = "reactionHarvestQueue"
    queryLimit = 4000

    #@facebookLogger.debug(showArgs=True)
    def method(self, nodeList):
        cursor = ClientItterator("%s/reactions" % nodeList[0]._ident, limit=self.queryLimit)
        retrieved_reactions = []
        jObject = cursor.next()
        while jObject:
            if threadsExitFlag[0]: return
            #pretty(jObject)
            fbProfile, new = FBProfile.objects.get_or_create(_ident=jObject['id'])
            if new:
                profileUpdateQueue.put(fbProfile)
            if isinstance(nodeList[0], FBPost):
                reaction, new = FBReaction.objects.get_or_create(
                    from_profile=fbProfile,
                    to_post=nodeList[0],
                    type=jObject['type']
                )
            elif isinstance(nodeList[0], FBComment):
                reaction, new = FBReaction.objects.get_or_create(
                    from_profile=fbProfile,
                    to_comment=nodeList[0],
                    type=jObject['type']
                )
            else: raise Exception("can only harvest reactions to FBPost and FBComment")
            retrieved_reactions.append(reaction)
            jObject = cursor.next()
        for reaction in nodeList[0].reactions.filter(until_time__isnull=True):
            if reaction not in retrieved_reactions:
                reaction.until_time = today()
                reaction.save()
        nodeList[0].last_reaction_harvested = today()
        nodeList[0].save()

