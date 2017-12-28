# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0011_talk_status_data_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True,
                                        auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1024)),
                ('order', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='talk',
            name='track',
            field=models.ForeignKey(null=True, blank=True, default=None,
                                    to='talks.Track',
                                    on_delete=models.SET_NULL),
            preserve_default=False,
        ),
    ]
