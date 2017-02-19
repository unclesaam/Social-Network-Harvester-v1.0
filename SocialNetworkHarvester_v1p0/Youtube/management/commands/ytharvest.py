from SocialNetworkHarvester_v1p0.settings import youtubeLogger
from django.core.management.base import BaseCommand
from tendo import singleton
from .harvest.harvest import harvestYoutube, send_routine_email, myEmailMessage, myEmailTitle
import datetime
from SocialNetworkHarvester_v1p0.settings import DEBUG, youtubeLogger
import time

now = datetime.datetime.now()

class Command(BaseCommand):
    help = 'Search the Youtube\'s API for new content'

    def handle(self, *args, **options):
        me = singleton.SingleInstance(flavor_id="cronyt")
        m = '%s: Will run the Youtube harvester' % now.strftime('%y-%m-%d_%H:%M')
        print(m)
        youtubeLogger.log(m)
        try:
            harvestYoutube()
        except:
            youtubeLogger.exception('YOUTUBE ROUTINE HAS ENCOUNTERED A TOP-LEVEL ERROR:')
        finally:
            print(myEmailTitle[0])
            print(myEmailMessage[0])
            youtubeLogger.log("The harvest has ended for the Youtube harvesters",showTime=True)
            if not DEBUG:
                send_routine_email(myEmailTitle[0], myEmailMessage[0])