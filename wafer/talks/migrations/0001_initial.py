# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import markitup.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('talk_id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('abstract', markitup.fields.MarkupField(help_text='Write two or three paragraphs describing your talk. Who is your audience? What will they get out of it? What will you cover?<br />You can use Markdown syntax.', no_rendered_field=True)),
                ('notes', models.TextField(help_text='Any notes for the conference organisers?', null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'A', b'Accepted'), (b'R', b'Not Accepted'), (b'P', b'Under Consideration')])),
                ('_abstract_rendered', models.TextField(editable=False, blank=True)),
                ('authors', models.ManyToManyField(related_name='talks', to=settings.AUTH_USER_MODEL)),
                ('corresponding_author', models.ForeignKey(related_name='contact_talks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TalkType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1024)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TalkUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256)),
                ('url', models.URLField()),
                ('talk', models.ForeignKey(to='talks.Talk')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='talk',
            name='talk_type',
            field=models.ForeignKey(to='talks.TalkType', null=True),
            preserve_default=True,
        ),
    ]
