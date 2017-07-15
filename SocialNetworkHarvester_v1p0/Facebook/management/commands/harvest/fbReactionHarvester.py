from .commonThread import *


class FbReactionHarvester(CommonThread):
    batchSize = 1
    workQueueName = "reactionHarvestQueue"
    queryLimit = 4000

    #@facebookLogger.debug(showArgs=True)
    def method(self, nodeList):
        node = nodeList[0]
        cursor = ClientItterator("%s/reactions" % node._ident, limit=self.queryLimit)
        retrieved_reactions = []
        try:
            jObject = cursor.next()
        except ClientException as e:
            if re.match(
                    r".*Object with ID '[0-9_]+' does not exist, cannot be loaded due to missing permissions, or does not support this operation\. .*", e.response['error']['message']):
                jObject.error_on_harvest = True
                jObject.save()
                log("could not harvest reactions from %s" % node)
                return
            else:
                raise
        while jObject:
            if threadsExitFlag[0]: return
            #pretty(jObject)
            fbProfile, new = FBProfile.objects.get_or_create(_ident=jObject['id'])
            if new:
                profileUpdateQueue.put(fbProfile)
            if isinstance(node, FBPost):
                reaction, new = FBReaction.objects.get_or_create(
                    from_profile=fbProfile,
                    to_post=node,
                    type=jObject['type']
                )
            elif isinstance(node, FBComment):
                reaction, new = FBReaction.objects.get_or_create(
                    from_profile=fbProfile,
                    to_comment=node,
                    type=jObject['type']
                )
            else: raise Exception("can only harvest reactions to FBPost and FBComment")
            retrieved_reactions.append(reaction)
            jObject = cursor.next()
        for reaction in node.reactions.filter(until_time__isnull=True):
            if reaction not in retrieved_reactions:
                reaction.until_time = today()
                reaction.save()
        node.last_reaction_harvested = today()
        node.save()

