# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0006_task_remove_date_start_time_end_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('nbr_volunteers_min', models.IntegerField(blank=True, null=True, default=1)),
                ('nbr_volunteers_max', models.IntegerField(blank=True, null=True, default=1)),
                ('video_task', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, to='volunteers.TaskCategory', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['start', '-end', 'template__name', 'name']},
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='nbr_volunteers_max',
            field=models.IntegerField(blank=True, null=True, default=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='nbr_volunteers_min',
            field=models.IntegerField(blank=True, null=True, default=1),
        ),
        migrations.AddField(
            model_name='task',
            name='template',
            field=models.ForeignKey(blank=True, to='volunteers.TaskTemplate', null=True),
        ),
    ]
