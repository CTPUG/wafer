# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import markitup.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('item', models.FileField(upload_to=b'pages_files')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(help_text='Last component of the page URL')),
                ('content', markitup.fields.MarkupField(help_text='Markdown contents for the page.', no_rendered_field=True)),
                ('include_in_menu', models.BooleanField(default=False, help_text='Whether to include in menus.')),
                ('exclude_from_static', models.BooleanField(default=False, help_text='Whether to exclude this page from the static version of the site (Container pages, etc.)')),
                ('_content_rendered', models.TextField(editable=False, blank=True)),
                ('files', models.ManyToManyField(help_text='Images and other files for use in the content markdown field.', related_name='pages', null=True, to='pages.File', blank=True)),
                ('parent', models.ForeignKey(
                    blank=True, to='pages.Page', null=True,
                    on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
