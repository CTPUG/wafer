# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0008_auto_20160629_1404'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='talktype',
            options={'ordering': ['order', 'id']},
        ),
        migrations.AddField(
            model_name='talktype',
            name='disable_submission',
            field=models.BooleanField(default=False, help_text=b"Don't allow users to submit talks of this type."),
        ),
        migrations.AddField(
            model_name='talktype',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]
