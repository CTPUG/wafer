# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0007_add_ordering_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='status',
            field=models.CharField(default=b'P', max_length=1, choices=[(b'A', b'Accepted'), (b'R', b'Not Accepted'), (b'C', b'Talk Cancelled'), (b'P', b'Under Consideration')]),
        ),
    ]
