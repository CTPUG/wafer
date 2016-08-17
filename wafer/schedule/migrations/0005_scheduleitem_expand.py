# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_drop_order_with_respect_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleitem',
            name='expand',
            field=models.BooleanField(
                default=False,
                help_text='Expand to neighbouring venues'),
        ),
    ]
