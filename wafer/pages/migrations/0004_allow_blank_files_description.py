# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_non-null_people+files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
