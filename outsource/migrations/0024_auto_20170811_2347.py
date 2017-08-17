# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-11 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0023_auto_20170811_2303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='options',
        ),
        migrations.AddField(
            model_name='beverageoption',
            name='order',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='outsource.Order'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='beverageoption',
            name='beverage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='outsource.Beverage'),
        ),
    ]