# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0005_sponsorshippackage_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
