# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-23 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0039_beverage_is_best'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='min_time',
            field=models.IntegerField(default=0),
        ),
    ]