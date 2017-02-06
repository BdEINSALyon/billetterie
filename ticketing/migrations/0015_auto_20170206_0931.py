# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-06 08:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0014_entry_selling_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='email_background_color',
            field=models.CharField(default='#3C121C', max_length=7),
        ),
        migrations.AddField(
            model_name='event',
            name='email_button_color',
            field=models.CharField(default='#6D1928', max_length=7),
        ),
        migrations.AddField(
            model_name='event',
            name='email_important_information_html',
            field=models.TextField(blank=True, default='<h2  class="align-center">Informations importantes</h2><p class="align-center">Ouverture des portes&nbsp;: 22h00</p><p class="align-center">Dernière entrée&nbsp;: <b>02h30</b></p>', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='email_more_info_link',
            field=models.CharField(blank=True, default='http://bal.bde-insa-lyon.fr', max_length=2500, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='logo_url',
            field=models.CharField(blank=True, default='http://logos.bde-insa-lyon.fr/bal/Logo_bal.png', max_length=2500, null=True),
        ),
    ]