# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL)
    ]

    operations = [
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=64, db_index=True)),
                ('value', jsonfield.fields.JSONField()),
                ('group', models.ForeignKey(
                    to='auth.Group', on_delete=models.CASCADE)),
            ],
        ),
    ]
