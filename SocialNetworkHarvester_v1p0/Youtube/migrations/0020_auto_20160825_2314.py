# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-26 03:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Youtube', '0019_auto_20160825_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ytcomment',
            name='text',
            field=models.CharField(max_length=8192, null=True),
        ),
    ]