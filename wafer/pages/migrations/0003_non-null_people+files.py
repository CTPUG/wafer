# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_page_people'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='files',
            field=models.ManyToManyField(help_text='Images and other files for use in the content markdown field.', related_name='pages', to='pages.File', blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='people',
            field=models.ManyToManyField(help_text='People associated with this page for display in the schedule (Session chairs, panelists, etc.)', related_name='pages', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
