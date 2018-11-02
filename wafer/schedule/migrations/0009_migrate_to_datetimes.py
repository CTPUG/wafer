# -*- coding: utf-8 -*-
# Manual migration to convert the data to appropriate datetimes
# Days are converted to blocks that run from day, 00:00:00 until 23:59:59
# Venue days are replaced with the appropriate schedule block
# slot times are converted to the correct (day, time) pairs
# We force the timezone to utc for this conversion.
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wafer.snippets.markdown_field


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_add_schedule_block_and_datetimes'),
    ]

    operations = [
    #    migrations.CreateModel(
    #        name='ScheduleBlock',
    #        fields=[
    #            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
    #            ('start_time', models.DateTimeField(blank=True, null=True)),
    #            ('end_time', models.DateTimeField(blank=True, null=True)),
    #        ],
    #        options={
    #            'ordering': ['start_time'],
    #        },
    #    ),
    #    migrations.AlterModelOptions(
    #        name='slot',
    #        options={'ordering': ['end_time', 'start_time']},
    #    ),
    #    migrations.RemoveField(
    #        model_name='slot',
    #        name='day',
    #    ),
    #    migrations.RemoveField(
    #        model_name='venue',
    #        name='days',
    #    ),
    #    migrations.RemoveField(
    #        model_name='slot',
    #        name='start_time',
    #    ),
    #    migrations.RemoveField(
    #        model_name='slot',
    #        name='end_time',
    #    ),
    #    migrations.AddField(
    #        model_name='slot',
    #        name='end_time',
    #        field=models.DateTimeField(help_text='Slot end time', null=True),
    #    ),
    #    migrations.AddField(
    #        model_name='slot',
    #        name='start_time',
    #        field=models.DateTimeField(blank=True, help_text='Start time (if no previous slot selected)', null=True),
    #    ),
    #    migrations.AlterField(
    #        model_name='slot',
    #        name='previous_slot',
    #        field=models.ForeignKey(blank=True, help_text='Previous slot if applicable (slots should have either a previous slot OR a day and start time set)', null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.Slot'),
    #    ),
    #    migrations.DeleteModel(
    #        name='Day',
    #    ),
    #    migrations.AddField(
    #        model_name='venue',
    #        name='blocks',
    #        field=models.ManyToManyField(help_text='Blocks (days) on which this venue will be used.', to='schedule.ScheduleBlock'),
    #    ),
    ]
