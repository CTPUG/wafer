# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0004_add_location'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['start', '-end', 'name']},
        ),
        migrations.AddField(
            model_name='task',
            name='end',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='start',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
