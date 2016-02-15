# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_auto_20150813_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
