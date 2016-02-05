from django.db import models
from django.utils.timezone import now as djangoNow
from django.utils.timezone import utc
from datetime import datetime

class time_label(models.Model):
    recorded_time = models.DateTimeField(default=djangoNow().replace(
            hour=0,minute=0,second=0,microsecond=0,tzinfo=utc))
    class Meta:
        abstract = True

class Integer_time_label(time_label):
    value = models.IntegerField()
    class Meta:
        abstract = True

class Text_time_label(time_label):
    value = models.TextField()
    class Meta:
        abstract = True

class Char_time_label(time_label):
    value = models.CharField(max_length=500)
    class Meta:
        abstract = True

class Boolean_time_label(time_label):
    value = models.BooleanField(default=False)
    class Meta:
        abstract = True
