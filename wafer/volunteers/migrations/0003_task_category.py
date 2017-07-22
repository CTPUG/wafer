# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0002_task_talk'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Task Category',
                'verbose_name_plural': 'Task Categories',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='category',
            field=models.ForeignKey(blank=True, null=True, to='volunteers.TaskCategory'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='preferred_categories',
            field=models.ManyToManyField(blank=True, to='volunteers.TaskCategory'),
        ),
    ]
