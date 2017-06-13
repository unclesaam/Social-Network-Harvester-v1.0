from django.db import models
from django.utils.timezone import now
from django.utils.timezone import utc
from datetime import datetime

def djangoNow():
    return now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=utc)

class time_label(models.Model):
    recorded_time = models.DateTimeField(default=djangoNow)
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'recorded_time':{
            'name':'Recorded time',
            'description': 'Time at wich the value has been observed.'
        }}

    def get_obj_ident(self):
        return "%s__%s" % (type(self).__name__,self.pk)

class Integer_time_label(time_label):
    value = models.IntegerField()
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Integer value that has been recorded at a point in time'
        }}.join(super(Integer_time_label,self).get_fields_description())


class Float_time_label(time_label):
    value = models.FloatField()

    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Float value that has been recorded at a point in time'
        }}.join(super(Float_time_label, self).get_fields_description())

class Big_integer_time_label(time_label):
    value = models.BigIntegerField()

    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Big integer value that has been recorded at a point in time'
        }}.join(super(Big_integer_time_label, self).get_fields_description())

class Text_time_label(time_label):
    value = models.TextField()
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Text value that has been recorded at a point in time'
        }}.join(super(Text_time_label,self).get_fields_description())

class Char_time_label(time_label):
    value = models.CharField(max_length=500)
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Char value that has been recorded at a point in time'
        }}.join(super(Char_time_label,self).get_fields_description())

class Boolean_time_label(time_label):
    value = models.BooleanField(default=False)
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {'value': {
            'name': 'Value',
            'description': 'Boolean value that has been recorded at a point in time'
        }}.join(super(Boolean_time_label,self).get_fields_description())

class Image_time_label(time_label):
    ''' Saves an image
    '''
    url = models.CharField(max_length=1024)
    location_on_disc = models.CharField(max_length=1024)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)

    def get_fields_description(self):
        return {'url': {
                'name': 'URL',
                'description': 'Url of origin of the image'},
            'title': {
                'name': 'Title',
                'description': 'Title of the image'},
            'description': {
                'name': 'Description',
                'description': 'Description of the image'},
            }.join(super(Image_time_label, self).get_fields_description())

class Video_time_label(time_label):
    ''' Saves a video
    '''
    url = models.CharField(max_length=1024)
    location_on_disc = models.CharField(max_length=1024)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)

    def get_fields_description(self):
        return {'url': {
            'name': 'URL',
            'description': 'Url of origin of the video'},
            'title': {
                'name': 'Title',
                'description': 'Title of the video'},
            'description': {
                'name': 'Description',
                'description': 'Description of the video'},
        }.join(super(Video_time_label, self).get_fields_description())

class Website_time_label(time_label):
    ''' Screencap a website frontpage in time
    '''
    # TODO: Implement web page scrapping
    pass


##################### GENERIC ASPIRA MODEL #########################

class GenericModel(models.Model):
    class Meta:
        abstract = True

    def get_fields_description(self):
        return {}

    def get_obj_ident(self):
        return "%s__%s" % (type(self).__name__,self.pk)

    def update(self, jObject):
        if not isinstance(jObject, dict):
            raise Exception('A DICT or JSON object must be passed as argument.')
        self.copyBasicFields(jObject)
        self.updateStatistics(jObject)

    def copyBasicFields(self, jObject):
        for attr in self.basicFields:
            if self.basicFields[attr][0] in jObject:
                val = jObject[self.basicFields[attr][0]]
                for key in self.basicFields[attr][1:]:
                    if key in val:
                        val = val[key]
                    else:
                        val = None
                if val:
                    setattr(self, attr, val)

    def updateStatistics(self, jObject):
        for attrName in self.statistics:
            countObjs = getattr(self, attrName).order_by('-recorded_time')
            objType = countObjs.model
            val = jObject
            for key in self.statistics[attrName]:
                if key in val:
                    val = val[key]
                else:
                    val = None
                    break
            if val:
                if not countObjs.exists():
                    objType.objects.create(**{self.reference_name:self, "value":val})
                else:
                    if countObjs[0].value != int(val) and countObjs[0].recorded_time != today():
                        objType.objects.create(**{self.reference_name:self, "value":val})




################## UTILS #####################

def removeEmojisFromFields(obj, fieldList, replacement=''):
    """
    Filter model instance for emojis to remove, given a list of field names
    :param obj: Model instance to filter from
    :param fieldList: List of the model fields suceptible to have emojis
    :param replacement: (optional): Character to replace emojis with
    :return: None
    """
    antiEmojiRegex = re.compile(u'['
                                u'\U0001F300-\U0001F64F'
                                u'\U0001F680-\U0001F6FF'
                                u'\u2600-\u26FF\u2700-\u27BF]+',
                                re.UNICODE)
    for field in fieldList:
        badStr = getattr(obj, field)
        if badStr:
            try:
                newStr = antiEmojiRegex.sub(badStr, replacement)
            except:
                newStr = antiEmojiRegex.sub(badStr[:-2], replacement) #TODO: Better error management
            setattr(obj, field, newStr)