from django import template
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
        if 'rules' in fieldVal and 'admin_only' in fieldVal['rules']:
            if not user.is_staff:
                continue
            else:
                toolTipText = ""
        elif 'description' in fieldVal:
            toolTipText = '<span class="tooltiptext">'+fieldVal['description']+'</span>'
        else:
            raise Exception('field "%s" contains no description')
        if getattr(instance, fieldName) == None: continue
        strVal = str(getattr(instance, fieldName))
        if 'type' not in fieldVal:
            raise Exception ('Field named "%s" as no declared type'%field)
        if "rules" in fieldVal and 'no_show' in fieldVal['rules']:
            continue
        elif fieldVal['type'] == 'integer':
            fontSize = 18
            if len(strVal) > 19:
                fontSize = 14
            if len(strVal) > 11:
                fontSize = 10
            if len(strVal) > 13:
                fontSize = 9
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value integer_value'>" \
                            "<span style='font-size:"+str(fontSize)+"px;'>"+strVal+"</span>"\
                        "</div>" \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+
                    '</div>')
        elif fieldVal['type'] == 'boolean':
            if strVal == 'False': strVal = "<span style='color:red'>Non</span>"
            else: strVal = "<span style='color:green'>Oui</span>"
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value boolean_value'>"+strVal+"</div>"+ \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'short_string':
            DOM.append('<div class="tooltip grid-item">'+ \
                    "<div class='value string_value'><span>"+strVal+"</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'long_string':
            if len(strVal) <= 35:
                grid_classes = "grid-item "
            elif len(strVal) <= 75:
                grid_classes = "grid-item grid-item--width2 "
            elif len(strVal) <= 315:
                grid_classes = "grid-item grid-item--width2 grid-item--height2"
            else:
                grid_classes = "grid-item grid-item--width3 grid-item--height2"
            DOM.insert(0,"<div class='tooltip "+grid_classes+"'>"\
                            "<div class='value string_value'><span>"+strVal+"</span></div>"\
                            "<div class='fieldName'>" \
                                "<span>"+fieldVal['name']+"</span>" \
                            "</div>" +\
                            toolTipText+\
                        '</div>')
        elif fieldVal['type'] == 'image_url':
            DOM.append('<div class="tooltip grid-item grid-item--width2 grid-item--height2" '
                       'style="background-image:url('+strVal+');">'+ \
                    "<div class='value image_value'></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'link_url':
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value link_url_value'><span>" \
                            "<a href='"+strVal+"' class='TableToolLink' target='_blank'>Lien</a>" \
                        "</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'date':
            DOM.append("<div class='tooltip grid-item'>"+ \
                    "<div class='value date_value'><span>"+strVal+"</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        else:
            raise Exception('Unrecognized field type: %s'%fieldVal['type'])
    #random.shuffle(DOM)
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