# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_number', models.CharField(max_length=16, null=True, blank=True)),
                ('bio', models.TextField(null=True, blank=True)),
                ('homepage', models.CharField(max_length=256, null=True, blank=True)),
                ('twitter_handle', models.CharField(max_length=15, null=True, blank=True)),
                ('github_username', models.CharField(max_length=32, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
