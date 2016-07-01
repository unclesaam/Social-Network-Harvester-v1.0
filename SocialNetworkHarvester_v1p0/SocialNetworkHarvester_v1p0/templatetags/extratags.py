from django import template
from collections import OrderedDict
register = template.Library()
from Twitter.models import TWUser,Hashtag,Tweet

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

@register.filter
def sort(value):
    return sorted(value)

@register.filter
def getFields(className):
    fields = globals()[className]().get_fields_description()
    keys = fields.keys()
    orderedFields = []
    for key in sorted(keys):
        orderedFields.append((key,fields[key]))
    return orderedFields