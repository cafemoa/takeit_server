# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-08 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0048_auto_20180103_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='is_making',
            field=models.BooleanField(default=False),
        ),
    ]