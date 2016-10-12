from SocialNetworkHarvester_v1p0.settings import twitterLogger
from django.core.management.base import BaseCommand
from tendo import singleton
from .harvest.harvest import harvestTwitter, send_routine_email, EmailMessage, EmailTitle
from SocialNetworkHarvester_v1p0.settings import twitterLogger, DEBUG
import datetime

now = datetime.datetime.now()

class Command(BaseCommand):
    help = 'Search the Twitter\'s API for new content'

    def handle(self, *args, **options):
        me = singleton.SingleInstance(flavor_id="crontw")
        print('%s: Will run the Twitter harvester'%now.strftime('%y-%m-%d_%H:%M'))
        twitterLogger.log("Will run the Twitter harvesters.")
        try:
            harvestTwitter()
        except:
            EmailMessage[0] = 'TWITTER HARVEST ROUTINE HAS ENCOUNTERED A TOP-LEVEL ERROR:'
            twitterLogger.exception(EmailMessage[0])
        finally:
            twitterLogger.log("The harvest has end for the Twitter harvesters.")
            if not DEBUG:
                send_routine_email(EmailTitle[0],lEmailMessage[0])
