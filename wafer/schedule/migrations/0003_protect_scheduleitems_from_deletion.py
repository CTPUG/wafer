# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140909_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleitem',
            name='venue',
            field=models.ForeignKey(to='schedule.Venue', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='slot',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='schedule.Day', help_text='Day for this slot', null=True),
        ),
    ]
