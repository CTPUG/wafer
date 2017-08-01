# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_task_min_nbr(apps, schema_editor):
    Task = apps.get_model('volunteers', 'Task')
    for task in Task.objects.all():
        if task.nbr_volunteers_min == 0:
            task.nbr_volunteers_min = 1
        if task.nbr_volunteers_max == 0:
            task.nbr_volunteers_max = 1
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0008_add_task_template'),
    ]

    operations = [
        migrations.RunPython(update_task_min_nbr),
    ]
