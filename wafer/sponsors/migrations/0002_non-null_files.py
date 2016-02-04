# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='files',
            field=models.ManyToManyField(help_text='Images and other files for use in the description markdown field.', related_name='sponsors', to='sponsors.File', blank=True),
        ),
        migrations.AlterField(
            model_name='sponsorshippackage',
            name='files',
            field=models.ManyToManyField(help_text='Images and other files for use in the description markdown field.', related_name='packages', to='sponsors.File', blank=True),
        ),
    ]
