# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-13 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0026_cafe_is_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='can_use_coupon',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='beverage',
            name='price',
            field=models.CharField(max_length=50),
        ),
    ]
