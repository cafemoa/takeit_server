# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-02 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0044_auto_20180102_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beverageoption',
            name='content',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='optionselection',
            name='content',
            field=models.CharField(max_length=100),
        ),
    ]
