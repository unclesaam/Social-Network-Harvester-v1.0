from .commonThread import *


class FbPageUpdater(CommonThread):
    batchSize = 25
    workQueueName = 'pageUpdateQueue'

    #@facebookLogger.debug(showArgs=True)
    def method(self, fbPageList):
        client = getClient()
        response = client.get("",
                ids=",".join([page._ident for page in fbPageList]),
                fields=[
                    "category", "name", "username", "about", "cover", "current_location", "description_html",
                    "display_subtext", "displayed_message_response_time", "emails", "featured_video", "general_info",
                    "impressum", "link", "members", "is_community_page", "is_unclaimed", "is_verified", "location",
                    "parent_page", "phone", "verification_status", "website", "checkins", "fan_count",
                    "overall_star_rating", "rating_count", "talking_about_count", "were_here_count", "birthday",
                    "affiliation", "personal_info", "personal_interests", "built", "features", "mpg", "company_overview",
                    "mission", "products", "founded", "general_manager", "price_range", "hours",
                    "pharma_safety_info", "is_permanently_closed", "is_always_open", "network", "schedule", "season",
                    "written_by", "awards", "directed_by", "genre", "plot_outline", "produced_by", "release_date",
                    "screenplay_by", "starring", "studio", "artists_we_like", "band_interests", "band_members", "bio",
                    "booking_agent", "hometown", "influences", "press_contact", "record_label",
                ]
            )
        returnClient(client)
        #pretty(response)
        for ident in response.keys():
            if threadsExitFlag[0]: return
            fbPage = FBPage.objects.get(_ident=ident)
            fbPage.update(response[ident])
            fbPageList = [fbPage for fbPage in fbPageList if fbPage._ident == ident]
        for fbPage in fbPageList:
            log("%s was not retrievable from facebook"% fbPage)
            fbPage.error_on_update = True
            fbPage.save()