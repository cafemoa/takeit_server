# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-25 08:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0002_auto_20170625_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cafe',
            name='orders',
        ),
        migrations.AlterField(
            model_name='order',
            name='cafe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='outsource.Cafe'),
        ),
    ]
