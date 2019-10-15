# -*- coding: utf-8 -*-
# Manual migration to cleanup old columns and models after migrating the data
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wafer.snippets.markdown_field


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_migrate_to_datetimes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slot',
            name='day',
        ),
        migrations.RemoveField(
            model_name='venue',
            name='days',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='old_start_time',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='old_end_time',
        ),
        migrations.DeleteModel(
            name='Day',
        ),
    ]
