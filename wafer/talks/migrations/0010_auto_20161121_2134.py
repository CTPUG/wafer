# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0009_auto_20160813_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='status',
            field=models.CharField(default=b'S', max_length=1, choices=[(b'A', b'Accepted'), (b'R', b'Not Accepted'), (b'C', b'Talk Cancelled'), (b'U', b'Under Consideration'), (b'S', b'Submitted'), (b'P', b'Provisionally Accepted')]),
        ),
    ]
