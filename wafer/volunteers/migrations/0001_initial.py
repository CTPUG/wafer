# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('nbr_volunteers_min', models.IntegerField(default=1)),
                ('nbr_volunteers_max', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['date', 'start_time', '-end_time', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('staff_rating', models.IntegerField(blank=True, null=True, choices=[(0, 'No longer welcome'), (1, 'Poor'), (2, 'Not great'), (3, 'Average'), (4, 'Good'), (5, 'Superb')])),
                ('staff_notes', models.TextField(blank=True, null=True)),
                ('tasks', models.ManyToManyField(blank=True, to='volunteers.Task')),
                ('user', models.OneToOneField(related_name='volunteer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='volunteers',
            field=models.ManyToManyField(blank=True, to='volunteers.Volunteer'),
        ),
    ]
