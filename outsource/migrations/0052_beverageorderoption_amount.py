# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-24 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0051_beverage_add_shot_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='beverageorderoption',
            name='amount',
            field=models.IntegerField(default=1),
        ),
    ]
