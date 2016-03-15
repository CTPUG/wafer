# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0003_talk_private_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='talk',
            options={'permissions': (('view_all_talks', 'Can see all talks'), ('edit_private_notes', 'Can edit the private notes fields'))},
        ),
    ]
