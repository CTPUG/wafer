# -*- coding: utf-8 -*-
# Manual migration to convert the data to appropriate datetimes
# Days are converted to blocks that run from day, 00:00:00 until 23:59:59
# Venue days are replaced with the appropriate schedule block
# slot times are converted to the correct (day, time) pairs
# We force the timezone to utc for this conversion.
from __future__ import unicode_literals

import datetime

from django.db import migrations
from django.utils import timezone

def convert_day_to_schedule_block(apps, schema_editor):
    """For each Day, create a schedule block with the
       time block running from 0:00 to 23:59:59."""
    Day = apps.get_model('schedule', 'Day')
    ScheduleBlock = apps.get_model('schedule', 'ScheduleBlock')
    for day in Day.objects.all():
        start_time = datetime.datetime(year=day.date.year,
                                       month=day.date.month,
                                       day=day.date.day,
                                       hour=0,
                                       minute=0,
                                       tzinfo=timezone.utc)
        end_time = datetime.datetime(year=day.date.year,
                                       month=day.date.month,
                                       day=day.date.day,
                                       hour=23,
                                       minute=59,
                                       second=59,
                                       tzinfo=timezone.utc)
        block = ScheduleBlock.objects.create(start_time=start_time,
                                             end_time=end_time)
        block.save()

def get_day(slot):
    """reimplement removed get_day helper method for migration"""
    if slot.day:
        return slot.day
    else:
        return get_day(slot.previous_slot)


def convert_slot_time_to_date_time(apps, schema_editor):
    """For each slot, convert the start and end times to datetimes"""
    Slot = apps.get_model('schedule', 'Slot')
    ScheduleBlock = apps.get_model('schedule', 'ScheduleBlock')
    for slot in Slot.objects.all():
        day = get_day(slot)
        if slot.old_start_time:
            new_start_time = datetime.datetime(year=day.date.year,
                                               month=day.date.month,
                                               day=day.date.day,
                                               hour=slot.old_start_time.hour,
                                               minute=slot.old_start_time.minute,
                                               second=slot.old_start_time.second,
                                               tzinfo=timezone.utc)
            slot.start_time = new_start_time
        new_end_time = datetime.datetime(year=day.date.year,
                                         month=day.date.month,
                                         day=day.date.day,
                                         hour=slot.old_end_time.hour,
                                         minute=slot.old_end_time.minute,
                                         second=slot.old_end_time.second,
                                         tzinfo=timezone.utc)
        slot.end_time = new_end_time
        slot.save()


def add_blocks_to_venues(apps, schema_editor):
    """For each slot and venue, add the ScheduleBlock corresponding to
       the existing day."""
    Venue = apps.get_model('schedule', 'Venue')
    ScheduleBlock = apps.get_model('schedule', 'ScheduleBlock')
    for venue in Venue.objects.all():
        for day in venue.days.all():
            start_time = datetime.datetime(year=day.date.year,
                                           month=day.date.month,
                                           day=day.date.day,
                                           hour=0,
                                           minute=0,
                                           tzinfo=timezone.utc)
            # Our earlier migration ensures this block exists
            block = ScheduleBlock.objects.filter(
                start_time__exact=start_time).first()
            venue.blocks.add(block)
        venue.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_add_schedule_block_and_datetimes'),
    ]

    operations = [
            migrations.RunPython(convert_day_to_schedule_block),
            migrations.RunPython(convert_slot_time_to_date_time),
            migrations.RunPython(add_blocks_to_venues),
    ]
