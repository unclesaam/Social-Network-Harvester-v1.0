# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-14 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Youtube', '0023_auto_20160912_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='ytplaylist',
            name='description',
            field=models.CharField(max_length=4096, null=True),
        ),
        migrations.AddField(
            model_name='ytplaylist',
            name='publishedAt',
            field=models.DateTimeField(null=True),
        ),
    ]
