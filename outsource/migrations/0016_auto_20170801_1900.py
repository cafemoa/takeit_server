# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-01 10:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0015_auto_20170801_1859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='beverage',
            new_name='beverages',
        ),
    ]
