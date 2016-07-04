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
