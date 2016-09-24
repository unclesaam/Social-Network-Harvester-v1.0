# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-21 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Youtube', '0007_auto_20160820_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='ytvideo',
            name='_deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='ytvideo',
            name='_error_on_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ytvideo',
            name='_last_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='ytvideo',
            name='_update_frequency',
            field=models.IntegerField(default=1),
        ),
    ]