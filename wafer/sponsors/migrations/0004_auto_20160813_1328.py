# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0003_add_ordering_option'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sponsor',
            options={'ordering': ['order', 'name', 'id']},
        ),
        migrations.AddField(
            model_name='sponsor',
            name='order',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='url',
            field=models.URLField(default=b'', help_text='Url to link back to the sponsor if required', blank=True),
        ),
    ]
