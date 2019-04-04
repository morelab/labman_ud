# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-16 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labman_setup', '0006_labmandeploygeneralsettings_base_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweetponyconfiguration',
            name='http_proxy',
        ),
        migrations.RemoveField(
            model_name='tweetponyconfiguration',
            name='https_proxy',
        ),
        migrations.RemoveField(
            model_name='tweetponyconfiguration',
            name='karmacracy_api_key',
        ),
        migrations.RemoveField(
            model_name='tweetponyconfiguration',
            name='karmacracy_username',
        ),
        migrations.AddField(
            model_name='labmandeploygeneralsettings',
            name='legal_information_url',
            field=models.URLField(null=True),
        ),
    ]
