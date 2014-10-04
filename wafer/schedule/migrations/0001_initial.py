# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wafer.snippets.markdown_field


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
        ('talks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduleItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('details', wafer.snippets.markdown_field.MarkdownTextField(help_text='Additional details (if required)', blank=True, add_html_field=False, allow_html=False, html_field_suffix=b'_html')),
                ('notes', models.TextField(help_text='Notes for the conference organisers', blank=True)),
                ('css_class', models.CharField(help_text='Custom css class for this schedule item', max_length=128, blank=True)),
                ('details_html', models.TextField(editable=False)),
                ('page', models.ForeignKey(blank=True, to='pages.Page', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(help_text='Start time (if no previous slot)', null=True, blank=True)),
                ('end_time', models.TimeField(help_text='Slot end time', null=True)),
                ('name', models.CharField(help_text='Identifier for use in the admin panel', max_length=1024, null=True, blank=True)),
                ('day', models.ForeignKey(blank=True, to='schedule.Day', help_text='Day for this slot', null=True)),
                ('previous_slot', models.ForeignKey(blank=True, to='schedule.Slot', help_text='Previous slot', null=True)),
            ],
            options={
                'ordering': ['end_time', 'start_time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=1024)),
                ('notes', wafer.snippets.markdown_field.MarkdownTextField(help_text='Notes or directions that will be useful to conference attendees', blank=True, add_html_field=False, allow_html=False, html_field_suffix=b'_html')),
                ('notes_html', models.TextField(editable=False)),
                ('days', models.ManyToManyField(help_text='Days on which this venue will be used.', to='schedule.Day')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name='slot',
            order_with_respect_to='day',
        ),
        migrations.AddField(
            model_name='scheduleitem',
            name='slots',
            field=models.ManyToManyField(to='schedule.Slot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduleitem',
            name='talk',
            field=models.ForeignKey(blank=True, to='talks.Talk', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scheduleitem',
            name='venue',
            field=models.ForeignKey(to='schedule.Venue'),
            preserve_default=True,
        ),
    ]
