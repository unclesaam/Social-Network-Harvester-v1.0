from django import template
from django.template.loader import render_to_string
from collections import OrderedDict
from Twitter.models import TWUser,Hashtag,Tweet,TWPlace, favorite_tweet, follower, HashtagHarvester
from Youtube.models import YTChannel, YTVideo, YTPlaylist, YTPlaylistItem, YTComment
from Facebook.models import FBUser, FBPage, FBPost, FBComment,FBReaction
import re
import random, emoji
import inspect

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
        if 'options' in fields[key]:
            options = fields[key]["options"]
            if any([
                ("downloadable" in options and not options["downloadable"]),
                ("admin_only" in options and options['admin_only'])
            ]):
                continue
        orderedFields.append((key,fields[key]))
    return orderedFields


@register.filter
def getFieldsAsDict(className):
    fields = globals()[className]().get_fields_description()
    return fields

@register.filter
def getFieldsValuesAsTiles(instance,user):
    '''
    Represents a model instance (FBPage, TWUser, etc) as a serie of "tiles", to be displayed using a masonry layout in
    their respective pages.
    :param instance: The model instance to represent
    :param user: The currently logged-in Aspira user
    :return: A string representing DOM objects (HTML elements with associated CSS classes)
    '''
    class Tile:

        value = None
        strValue = ""
        name = ""
        type = None
        options = {}
        description = ""
        extra_class = ""
        extra_features = ""
        DOM = ""

        def __init__(self, fieldName, fieldVal):
            self.fieldName = fieldName
            self.fieldVal = fieldVal
            log(fieldName)
            if self.parseValue() and\
                    self.parseName() and \
                    self.parseOptions() and \
                    self.parseType() and \
                    self.parseDescription() and\
                    self.parseClass():
                self.generate()

        def parseValue(self):
            self.value = getattr(instance, fieldName)
            if self.value is None: return False
            value = self.value
            if inspect.ismethod(value):
                value = value()
            self.strValue = emoji.emojize(str(value))
            if self.strValue == "": return False
            return True

        def parseName(self):
            if not "name" in self.fieldVal:
                raise Exception('%s\'s field "%s" must have a declared name.'%(
                        self.instance.__class__.__name__, fieldName))
            self.name = self.fieldVal['name']
            return True

        def parseOptions(self):
            if "options" in self.fieldVal:
                self.options = self.fieldVal['options']
                if "description" not in self.fieldVal and any([
                    ("admin_only" not in self.options)
                ]):
                    raise Exception('field "%s" must contain a description or declare "admin_only" in its options"')

                if "admin_only" in self.options and self.options['admin_only']:
                    if not user.is_staff:
                        return False
                    else:
                        self.extra_class += "admin_only_value "
                        self.description = "Value only visible by administrators"
                if 'displayable' in self.options and not self.options['displayable']:
                    return False
            return True

        def parseType(self):
            if not "type" in self.fieldVal:
                raise Exception('Model %s\'s field "%s" must have a declared type'%
                                (instance.__class__.__name__, fieldName))
            self.type = self.fieldVal['type']
            if self.type not in ['link_url','html_link','date','integer','boolean','short_string','long_string',
                                 'image_url','object_list','object']:
                raise Exception('Unrecognized field type for %s\'s field "%s": "%s"' %(
                        instance.__class__.__name__, fieldName,self.fieldVal['type']))
            return True

        def parseClass(self):
            if self.type == "object":
                if not hasattr(self.value, "getLink"):
                    raise Exception('Model "%s" must implement the "getLink" method'%self.value.__class__.__name__)
                if self.value.getLink() is None:
                    return False
            if self.type in ["long_string","object"]:
                strValue = str(self.value)
                if strValue == "": return False
                if len(strValue) <= 30:
                    pass
                elif len(strValue) <= 70:
                    self.extra_class += "grid-item--width2 "
                elif len(strValue) <= 315:
                    self.extra_class += "grid-item--width2 grid-item--height2 "
                else:
                    self.extra_class += "grid-item--width3 grid-item--height2 "
            elif self.type == "image_url":
                self.extra_class += "grid-item--width2 grid-item--height2"
                self.extra_features += 'style="background-image:url('+self.value+'); background-size:cover;"' \
                                                    'onclick = displayCenterPopup("imageBigDisplayPopup")'
            elif self.type == 'object_list':
                if self.value.count() == 0: return False
                if not hasattr(self.value.first(), "getLink"):
                    raise Exception('Model "%s" must implement the "getLink" method' %
                                    self.value.first().__class__.__name__)
                if self.value.first().getLink() is None: return False
                if self.value.count() <= 2:
                    self.extra_class += "grid-item--width2 "
                elif self.value.count() <= 4:
                    self.extra_class += "grid-item--width2 grid-item--height2 "
                else:
                    self.extra_class += "grid-item--width3 grid-item--height2 "
            return True

        def parseDescription(self):
            if 'description' in self.fieldVal:
                self.description = self.fieldVal['description']
            return True

        def generate(self):
            self.DOM = render_to_string('tool/misc.html', context={
                "tool": "gridDisplayItem",
                "field":self
            })

    fields = instance.get_fields_description()
    long_text_tiles = []
    short_text_tiles = []
    admin_only_tiles = []
    for fieldName, fieldVal in sorted(fields.items()):
        tile = Tile(fieldName, fieldVal)
        if "height2" in tile.extra_class:
            long_text_tiles.append(tile)
        elif "admin_only_value" in tile.extra_class:
            admin_only_tiles.append(tile)
        else:
            short_text_tiles.append(tile)
    ret = '<div class="grid-sizer"></div>'
    for tile in long_text_tiles + short_text_tiles + admin_only_tiles:
        ret += tile.DOM
    return ret



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