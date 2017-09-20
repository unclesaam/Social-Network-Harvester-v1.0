from .commonThread import *


class FbStatusUpdater(CommonThread):
    batchSize = 25
    workQueueName = 'statusUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbStatusList):
        client = getClient()
        response = client.get("",
                ids=",".join([status._ident for status in fbStatusList]),
                fields=['admin_creator','caption','created_time','description','from','to',
                        'is_hidden','is_instagram_eligible','link','message',"message_tags",'story',
                        'name','object_id','parent_id','permalink_url','picture','source','status_type','type',
                        'updated_time','shares','likes.limit(0).summary(true),comments.limit(0).summary(true)',
                ]
            )
        #pretty(response)
        returnClient(client)

        for ident, item in response.items():
            if threadsExitFlag[0]: return
            fbPost = FBPost.objects.get(_ident=ident)
            self.setParentPost(fbPost, item)
            self.setAuthor(fbPost, item)
            self.setToProfile(fbPost, item)
            self.setTags(fbPost, item)
            fbPost.update(item)
        for fbPost in fbStatusList:
            if fbPost._ident not in response.keys():
                log("%s was not retrievable from facebook"% fbPost)
                fbPost.error_on_update = True
                fbPost.save()


    def setParentPost(self,fbPost, jObject):
        if "parent_id" in jObject:
            post, new = FBPost.objects.get_or_create(_ident=jObject['parent_id'])
            if new:
                statusUpdateQueue.put(post)
            fbPost.parent_post = post

    def setAuthor(self,fbPost, jObject):
        if "from" in jObject and "id" in jObject["from"]:
            profile, new = FBProfile.objects.get_or_create(_ident=jObject['from']['id'])
            if new:
                profileUpdateQueue.put(profile)
            fbPost.from_profile = profile

    def setToProfile(self,fbPost, jObject):
        if "to" in jObject and 'data' in jObject['to']:
            for jTarget in jObject['to']['data']:
                profile, new = FBProfile.objects.get_or_create(_ident=jTarget['id'])
                if new:
                    profileUpdateQueue.put(profile)
                fbPost.to_profiles.add(profile)

    def setTags(self,fbPost, jObject):
        if "message_tags" in jObject:
            for jTag in jObject['message_tags']:
                if 'type' in jTag and jTag['type'] in ['user','page','group','event','application']:
                    profile, new = FBProfile.objects.get_or_create(_ident=jTag['id']) # Keeps only "profile" references
                    if new:
                        profile.createAndSetInstance(jTag['type'])
                        profileUpdateQueue.put(profile)
                    fbPost.message_tags.add(profile)
                else:
                    log("unrecognized jTag: %s"%jTag)
                    #TODO: create generic FBObjects that can represent anything