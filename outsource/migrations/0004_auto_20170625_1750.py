# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-25 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0003_auto_20170625_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='last_coupon_update',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
