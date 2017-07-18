# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='talk',
            field=models.ForeignKey(blank=True, null=True, to='talks.Talk'),
        ),
    ]
