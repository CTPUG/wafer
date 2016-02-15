# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kv', '__first__'),
        ('talks', '0004_edit_private_notes_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='kv',
            field=models.ManyToManyField(to='kv.KeyValue'),
        ),
    ]
