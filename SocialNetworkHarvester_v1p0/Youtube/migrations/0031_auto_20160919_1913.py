# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-19 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Youtube', '0030_auto_20160916_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ytchannel',
            name='description',
            field=models.CharField(max_length=8192, null=True),
        ),
    ]
