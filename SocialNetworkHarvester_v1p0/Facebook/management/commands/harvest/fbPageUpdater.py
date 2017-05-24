from .commonThread import *


class FbPageUpdater(CommonThread):
    batchSize = 1           # number of pages requested at once
    fieldsPerChunk = 1      # number of fields requested in each API call
    workQueueName = 'pageUpdateQueue'
    allFields = [
        "rating_count","category", "name", "username", "about", "cover", "current_location", "description_html",
        "display_subtext", "displayed_message_response_time", "emails", "featured_video", "general_info",
        "impressum", "link", "members", "is_community_page", "is_unclaimed", "is_verified", "location",
        "parent_page", "phone", "verification_status", "website", "checkins", "fan_count",
        "talking_about_count", "were_here_count", "birthday","overall_star_rating",
        "affiliation", "personal_info", "personal_interests", "built", "features", "mpg",
        "company_overview","mission", "products", "founded", "general_manager", "price_range", "hours",
        "pharma_safety_info", "is_permanently_closed", "is_always_open", "network", "schedule", "season",
        "written_by", "awards", "directed_by", "genre", "plot_outline", "produced_by", "release_date",
        "screenplay_by", "starring", "studio", "artists_we_like", "band_interests", "band_members", "bio",
        "booking_agent", "hometown", "influences", "press_contact", "record_label"
    ]

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbPageList):

        response = self.gatherInfos(fbPageList)

        for ident in response.keys():
            if threadsExitFlag[0]: return
            fbPage = FBPage.objects.get(_ident=ident)
            fbPage.update(response[ident])
        for fbPage in fbPageList:
            if fbPage._ident not in response.keys():
                log("%s was not retrievable from facebook"% fbPage)
                fbPage.error_on_update = True
                fbPage.save()

    def gatherInfos(self, fbPageList):
        responses = []
        client = getClient()
        for fieldList in [self.allFields[x:x + self.fieldsPerChunk] for x in range(
                0, len(self.allFields), self.fieldsPerChunk)]:
            try:
                responses.append(client.get("",
                                            ids=",".join([page._ident for page in fbPageList]), fields=fieldList))
            except:
                log('Facebook API rejected fields %s'% fieldList)
        returnClient(client)
        return mergeDicts(responses)


def mergeDicts(dictList):
    result = {}
    for d in dictList:
        for key, value in d.items():
            if not key in result: result[key] = {}
            for subKey, subValue in value.items():
                result[key][subKey] = subValue
    return result