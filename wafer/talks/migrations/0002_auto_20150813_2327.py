# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='talk',
            options={'permissions': (('view_all_talks', 'Can see all talks'),)},
        ),
    ]
