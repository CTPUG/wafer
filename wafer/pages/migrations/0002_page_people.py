# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='people',
            field=models.ManyToManyField(help_text='People associated with this page for display in the schedule (Session chairs, panelists, etc.)', related_name='pages', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
