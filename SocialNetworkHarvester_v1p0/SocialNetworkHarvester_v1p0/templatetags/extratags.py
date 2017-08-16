from django import template
from collections import OrderedDict
from Twitter.models import TWUser,Hashtag,Tweet,TWPlace, favorite_tweet, follower, HashtagHarvester
from Youtube.models import YTChannel, YTVideo, YTPlaylist, YTPlaylistItem, YTComment
from Facebook.models import FBUser, FBPage, FBPost, FBComment,FBReaction
import re

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
def getFieldsValuesAsTiles(instance):
    fields = instance.get_fields_description()
    DOM = ""
    for fieldName, fieldVal in fields.items():
        if getattr(instance, fieldName) == None: continue
        strVal = str(getattr(instance, fieldName))
        if 'type' not in fieldVal:
            pass
            #raise Exception ('Field named "%s" as no declared type'%field)
        elif fieldVal['type'] == 'integer':
            fontSize = 18
            if len(strVal) > 19:
                fontSize = 14
            if len(strVal) > 11:
                fontSize = 10
            if len(strVal) > 13:
                fontSize = 9
            DOM += '<div class="overviewValue tooltip">'+ \
                        "<div class='value integer_value'>" \
                            "<span style='font-size:"+str(fontSize)+"px;'>"+strVal+"</span>"\
                        "</div>" \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+\
                        '<span class="tooltiptext">'+ \
                            fieldVal['description']+\
                        '</span>'+\
                    '</div>'
        elif fieldVal['type'] == 'boolean':
            if strVal == 'False': strVal = "Faux"
            else: strVal = "Vrai"
            DOM +=  '<div class="overviewValue tooltip">'+ \
                        "<div class='value boolean_value'><span>"+strVal+"</span></div>"+ \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                        '<span class="tooltiptext">'+fieldVal['description']+'</span>'+ \
                    '</div>'
        elif fieldVal['type'] == 'short_string':
            DOM +=  '<div class="overviewValue tooltip">'+ \
                    "<div class='value string_value'><span>"+strVal+"</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                    '<span class="tooltiptext">'+fieldVal['description']+'</span>'+ \
                    '</div>'
        elif fieldVal['type'] == 'long_string':
            if len(strVal) <= 35:
                width=100; height=38 # base width and height
            elif len(strVal) <= 75:
                width=212; height=38 # double width
            elif len(strVal) <= 315:
                width=212; height=129 # double width and height
            else:
                width=324; height=129 # triple width, double height
            DOM +=  "<div class='overviewValue tooltip'>"\
                        "<div class='value string_value'  " \
                                "style='width:"+str(width)+"px;height:"+str(height)+"px;line-height:"+str(height)+"px;'>"\
                            "<span>"+strVal+"</span>" \
                        "</div>" \
                        "<div class='fieldName' style='width:"+str(width)+"px;'>" \
                            "<span>"+fieldVal['name']+"</span>" \
                        "</div>"\
                        '<span class="tooltiptext">'+fieldVal['description']+'</span>'+\
                    '</div>'
        else:
            raise Exception('Unrecognized field type: %s'%fieldVal['type'])
    return DOM



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