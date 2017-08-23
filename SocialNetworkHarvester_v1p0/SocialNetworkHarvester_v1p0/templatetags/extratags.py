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
        if getattr(instance, fieldName) is None: continue
        value = getattr(instance, fieldName)
        if 'options' in fieldVal:
            options = fieldVal['options']
            if 'admin_only' in options and options['admin_only'] and not user.is_staff:
                continue
            else:
                toolTipText = ""
            if 'displayable' in options and not options['displayable']:
                continue
            '''if 'subfield_display' in options:
                log(value)
                for subfield in re.split("__", options["subfield_display"]):
                    log(subfield)
                    if hasattr(value, subfield):
                        value = getattr(value, subfield)
                    else:
                        value = "NOPE"
                    if callable(value):
                        value = value()
                    log(value)'''
        elif 'description' in fieldVal:
            toolTipText = '<span class="tooltiptext">'+fieldVal['description']+'</span>'
        else:
            raise Exception('field "%s" contains no description')
        if fieldVal['type'] != 'object_list':
            value = str(value)
        if 'type' not in fieldVal:
            raise Exception ('Field named "%s" as no declared type'%fieldName)
        if "rules" in fieldVal and 'no_show' in fieldVal['rules']:
            continue
        elif value == "":
            continue
        elif fieldVal['type'] == 'integer':
            fontSize = 18
            if len(value) >= 15:
                fontSize = 8
            elif len(value) >= 13:
                fontSize = 9
            elif len(value) >= 11:
                fontSize = 10
            elif len(value) >= 9:
                fontSize = 12
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value integer_value'>" \
                            "<span style='font-size:"+str(fontSize)+"px;'>"+value+"</span>"\
                        "</div>" \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+
                    '</div>')
        elif fieldVal['type'] == 'boolean':
            if value == 'False': value = "<span style='color:red'>Non</span>"
            else: value = "<span style='color:green'>Oui</span>"
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value boolean_value'>"+value+"</div>"+ \
                        "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'short_string':
            DOM.append('<div class="tooltip grid-item">'+ \
                    "<div class='value string_value'><span>"+value+"</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'long_string':
            if len(value) <= 35:
                grid_classes = "grid-item "
            elif len(value) <= 75:
                grid_classes = "grid-item grid-item--width2 "
            elif len(value) <= 315:
                grid_classes = "grid-item grid-item--width2 grid-item--height2"
            else:
                grid_classes = "grid-item grid-item--width3 grid-item--height2"
            DOM.insert(0,"<div class='tooltip "+grid_classes+"'>"\
                            "<div class='value string_value'><span>"+value+"</span></div>"\
                            "<div class='fieldName'>" \
                                "<span>"+fieldVal['name']+"</span>" \
                            "</div>" +\
                            toolTipText+\
                        '</div>')
        elif fieldVal['type'] == 'image_url':
            DOM.append('<div class="tooltip grid-item grid-item--width2 grid-item--height2" '
                            'style="background-image:url('+value+');background-size:cover;" '
                            'onclick=displayCenterPopup("imageBigDisplayPopup")>'
                            '<div class="popup" id="imageBigDisplayPopup">'\
                            '   <div id="title">'+fieldVal['name']+'</div>'\
                            '   <div id="help">'+toolTipText+'</div>'\
                            '   <div id="content">'\
                            '       <img class="imageBigDisplay" src="'+value+'"></>'+\
                            '   </div>'\
                            '   <script id="functions">'\
                            '   </script>'
                            '</div>'+ \
                            "<div class='value image_value'></div>"+ \
                            "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                                toolTipText+ \
                        '</div>')
        elif fieldVal['type'] == 'link_url':
            DOM.append('<div class="tooltip grid-item">'+ \
                        "<div class='value link_url_value'><span>" \
                            "<a href='"+value+"' class='TableToolLink' target='_blank'>Lien</a>" \
                        "</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'date':
            DOM.append("<div class='tooltip grid-item'>"+ \
                    "<div class='value date_value'><span>"+value+"</span></div>"+ \
                    "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                       toolTipText+ \
                    '</div>')
        elif fieldVal['type'] == 'object_list':
            if value.count() == 0: continue
            values = [val for val in value.all()]
            tile = "<div class='tooltip grid-item grid-item--width2 grid-item--height2'>"+ \
                  "<div class='value object_list_value'><span><ul>"
            for val in values:
                tile += "<li><a href='"+val.getLink()+"' class='TableToolLink'>"+str(val)+"</a></li>"
            tile += "</ul></span></div>"+ \
                  "<div class='fieldName'><span>"+fieldVal['name']+"</span></div>"+ \
                  toolTipText+ \
                  '</div>'
            DOM.append(tile)
        else:
            raise Exception('Unrecognized field type: %s'%fieldVal['type'])
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