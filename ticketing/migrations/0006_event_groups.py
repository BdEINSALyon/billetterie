# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-02 23:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('ticketing', '0005_event_ticket_background'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='groups',
            field=models.ManyToManyField(to='auth.Group'),
        ),
    ]
