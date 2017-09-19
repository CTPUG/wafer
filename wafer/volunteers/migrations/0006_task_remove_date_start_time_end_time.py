# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0005_task_add_start_end'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='date',
        ),
        migrations.RemoveField(
            model_name='task',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='task',
            name='start_time',
        ),
        migrations.AlterField(
            model_name='task',
            name='end',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='start',
            field=models.DateTimeField(),
        ),
    ]
