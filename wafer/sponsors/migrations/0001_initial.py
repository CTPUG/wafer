# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
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
                ('item', models.FileField(upload_to=b'sponsors_files')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', markitup.fields.MarkupField(help_text='Write some nice things about the sponsor.', no_rendered_field=True)),
                ('_description_rendered', models.TextField(editable=False, blank=True)),
                ('files', models.ManyToManyField(help_text='Images and other files for use in the description markdown field.', related_name='sponsors', null=True, to='sponsors.File', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SponsorshipPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=255)),
                ('number_available', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(default=b'$', help_text='Currency symbol for the sponsorship amount.', max_length=16)),
                ('price', models.DecimalField(help_text='Amount to be sponsored.', max_digits=12, decimal_places=2)),
                ('short_description', models.TextField(help_text='One sentence overview of the package.')),
                ('description', markitup.fields.MarkupField(help_text='Describe what the package gives the sponsor.', no_rendered_field=True)),
                ('_description_rendered', models.TextField(editable=False, blank=True)),
                ('files', models.ManyToManyField(help_text='Images and other files for use in the description markdown field.', related_name='packages', null=True, to='sponsors.File', blank=True)),
            ],
            options={
                'ordering': ['order', '-price', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='packages',
            field=models.ManyToManyField(related_name='sponsors', to='sponsors.SponsorshipPackage'),
            preserve_default=True,
        ),
    ]
