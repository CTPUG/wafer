# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_scheduleitem_expand'),
        ('volunteers', '0003_task_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
                ('venue', models.ForeignKey(to='schedule.Venue', null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='location',
            field=models.ForeignKey(null=True, to='volunteers.TaskLocation'),
        ),
    ]
