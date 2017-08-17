# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-08 07:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0019_auto_20170807_2312'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeverageOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('whipping_cream', models.BooleanField(default=False)),
                ('is_ice', models.BooleanField(default=False)),
                ('size', models.IntegerField(default=0)),
                ('beverage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='outsource.Beverage')),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='beverage',
        ),
        migrations.AddField(
            model_name='event',
            name='beverages',
            field=models.ManyToManyField(blank=True, related_name='events', to='outsource.Beverage'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount_price',
            field=models.IntegerField(default=0),
        ),
    ]
