from SocialNetworkHarvester_v1p0.settings import twitterLogger
from django.core.management.base import BaseCommand
from tendo import singleton
from .harvest import harvestTwitter
from SocialNetworkHarvester_v1p0.settings import twitterLogger


class Command(BaseCommand):
    help = 'Search the Twitter\'s API for new content'

    def handle(self, *args, **options):
        me = singleton.SingleInstance(flavor_id="crontw")
        twitterLogger.log("Will run the Twitter harvesters.")
        try:
            harvestTwitter()
        except:
            twitterLogger.exception('TWITTER ROUTINE HAS ENCOUNTERED A TOP-LEVEL ERROR:')
        finally:
            twitterLogger.log("The harvest has end for the Twitter harvesters.")