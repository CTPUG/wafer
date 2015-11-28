# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0002_auto_20150813_2327'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='private_notes',
            field=models.TextField(help_text='Note space for the conference organisers (not visible to submitter)', null=True, blank=True),
            preserve_default=True,
        ),
    ]
