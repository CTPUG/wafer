# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import pytz

from django.db import migrations
from django.utils import timezone


def populate_start_end(apps, schema_editor):
    # Hardcoded as the live tasks were hardcoded to that timezone...
    tz = pytz.timezone('America/Montreal')
    Task = apps.get_model('volunteers', 'Task')
    for task in Task.objects.all():
        task.start = timezone.make_aware(datetime.datetime.combine(
            task.date, task.start_time), tz)
        task.end = timezone.make_aware(datetime.datetime.combine(
                task.date, task.end_time), tz)
        if task.end_time == datetime.time(0, 0):
            task.end += datetime.timedelta(days=1)
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0005_task_add_start_end'),
    ]

    operations = [
        migrations.RunPython(populate_start_end),
    ]
