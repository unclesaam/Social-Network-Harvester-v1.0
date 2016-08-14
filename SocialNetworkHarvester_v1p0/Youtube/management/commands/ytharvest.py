from SocialNetworkHarvester_v1p0.settings import youtubeLogger
from django.core.management.base import BaseCommand
from tendo import singleton
from .harvest.harvest import harvestYoutube
import datetime

now = datetime.datetime.now()

class Command(BaseCommand):
    help = 'Search the Youtube\'s API for new content'

    def handle(self, *args, **options):
        me = singleton.SingleInstance(flavor_id="crontw")
        print('%s: Will run the Youtube harvester' % now.strftime('%y-%m-%d_%H:%M'))
        youtubeLogger.log("Will run the Youtube harvesters.")
        try:
            harvestYoutube()
        except:
            youtubeLogger.exception('YOUTUBE ROUTINE HAS ENCOUNTERED A TOP-LEVEL ERROR:')
        finally:
            youtubeLogger.log("The harvest has end for the Youtube harvesters.")