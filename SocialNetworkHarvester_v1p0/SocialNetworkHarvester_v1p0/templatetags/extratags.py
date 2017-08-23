from django import template
from django.template.loader import render_to_string
from collections import OrderedDict
from Twitter.models import TWUser,Hashtag,Tweet,TWPlace, favorite_tweet, follower, HashtagHarvester
from Youtube.models import YTChannel, YTVideo, YTPlaylist, YTPlaylistItem, YTComment
from Facebook.models import FBUser, FBPage, FBPost, FBComment,FBReaction
import re
import random

register = template.Library()


from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG, STATICFILES_VERSION, FACEBOOK_APP_PARAMS

log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0

@register.filter
def sort(value):
    return sorted(value)

@register.filter
def getFields(className):
    '''Get the name and description of each relevant (downloadable) field of a given Aspira object.
    Use inside a template with:
    {% for key,val in 'className'|getFields %} ... {% endfor %}
    In order to work, the method "get_fields_description" should be implemented in the model
    :param className: The Class name of a given model. (example: "TWUser", "TWeet". "Hashtag", etc.)
    :return: a list of tuples, containing a string (field) and a dict {"name":"aName","description":"aDescription"}.
    '''
    fields = globals()[className]().get_fields_description()
    keys = fields.keys()
    orderedFields = []
    for key in sorted(keys):
        if 'options' in fields[key] and "downloadable" in fields[key]["options"] and \
                not fields[key]["options"]["downloadable"]:
            continue # By default, if the option "downloadable" is missing, the field is considered downloadable.
        orderedFields.append((key,fields[key]))
    return orderedFields


@register.filter
def getFieldsAsDict(className):
    fields = globals()[className]().get_fields_description()
    return fields

@register.filter
def getFieldsValuesAsTiles(instance,user):
    fields = instance.get_fields_description()
    DOM = []
    for fieldName, fieldVal in sorted(fields.items()):
        if getattr(instance, fieldName) is None: continue
        if not "type" in fieldVal:
            raise Exception('Model %s\'s field "%s" must have a declared type'%
                            (instance.__class__.__name__, fieldName))
        value = getattr(instance, fieldName)
        if 'options' in fieldVal:
            options = fieldVal['options']
            if 'admin_only' in options and options['admin_only'] and not user.is_staff:
                continue
            else:
                toolTipText = ""
            if 'displayable' in options and not options['displayable']:
                continue


        elif 'description' in fieldVal:
            toolTipText = '<span class="tooltiptext">'+fieldVal['description']+'</span>'
        else:
            raise Exception('field "%s" must contain a description')
        if 'type' not in fieldVal:
            raise Exception ('Field named "%s" has no declared type'%fieldName)
        valueType = fieldVal['type']
        if "rules" in fieldVal and 'no_show' in fieldVal['rules'] or value == "":
            continue
        if valueType not in ['link_url','date','integer',
                                'boolean','short_string','long_string',
                                'image_url','object_list','object']:
            raise Exception('Unrecognized field type: %s' % fieldVal['type'])

        context = {
            "tool": "gridDisplayItem",
            "value": value,
            "strValue":str(value),
            "fieldVal": fieldVal,
        }
        if valueType == "object":
            if not hasattr(value, "getLink"):
                raise Exception('Model "%s" must implement the "getLink" method'%value.__class__.__name__)
            if value.getLink() is None: continue
        if valueType in ["long_string","object"]:
            strValue = str(value)
            if len(strValue) <= 30:
                extra_class = ""
            elif len(strValue) <= 70:
                extra_class = "grid-item--width2 "
            elif len(strValue) <= 315:
                extra_class = "grid-item--width2 grid-item--height2"
            else:
                extra_class = "grid-item--width3 grid-item--height2"
            context['extra_class'] = extra_class
        elif valueType == "image_url":
            context['extra_class'] = "grid-item--width2 grid-item--height2"
            context['extra_components'] = 'style="background-image:url('+value+'); background-size:cover;"' \
                                           'onclick = displayCenterPopup("imageBigDisplayPopup")'
        elif valueType == 'object_list':
            if value.count() == 0: continue
            if not hasattr(value.first(), "getLink"):
                raise Exception('Model "%s" must implement the "getLink" method' %
                                value.first().__class__.__name__)
            if value.first().getLink() is None: continue
            if value.count() <= 2:
                context['extra_class'] = "grid-item--width2"
            elif value.count() <= 4:
                context['extra_class'] = "grid-item--width2 grid-item--height2"
            else:
                context['extra_class'] = "grid-item--width3 grid-item--height2"
        DOM.append(render_to_string('tool/misc.html', context=context))
    DOM.append('<div class="grid-sizer"></div>')
    return ''.join(DOM)


@register.filter
def join(string, arg):
    '''
    :param string: The string to be appended
    :return: joit string and args values
    '''
    return re.sub(" ","_", str(string) + str(arg))


@register.filter
def multiply(a, b):
    return a * b