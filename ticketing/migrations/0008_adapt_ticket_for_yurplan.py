# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-05 23:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0007_ticket_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='yurplanlink',
            old_name='yurplan_event',
            new_name='event_id',
        ),
        migrations.RemoveField(
            model_name='yurplanlink',
            name='yurplan_id',
        ),
        migrations.AddField(
            model_name='yurplanlink',
            name='order_id',
            field=models.IntegerField(default=0, verbose_name='Numéro de commande Yurplan'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='yurplanlink',
            name='order_reference',
            field=models.CharField(default=0, max_length=15, verbose_name='Référence de commande Yurplan'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='yurplanlink',
            name='token',
            field=models.CharField(default='YPTB0', help_text='Ce code est celui constituant le code bare du billet YurPlan', max_length=100, verbose_name='Clef du billet'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='yurplanlink',
            name='user_id',
            field=models.IntegerField(default=0, verbose_name='Utilisateur Yurplan'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='yurplanlink',
            name='yurplan_ticket_id',
            field=models.IntegerField(default=0, verbose_name='Identifiant du billet'),
            preserve_default=False,
        ),
    ]