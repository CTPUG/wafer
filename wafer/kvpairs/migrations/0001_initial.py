# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Key name')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Key owner group', to='auth.Group', null=True)),
                ('model_ct', models.ForeignKey(verbose_name=b'Referenced model type', to='contenttypes.ContentType')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name=b'Key owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Key',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KeyValuePair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_id', models.PositiveIntegerField(verbose_name=b'ID of referenced model instance')),
                ('value', models.CharField(max_length=65535, verbose_name=b'Value for key associated with model instance')),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name=b'Base key context', to='kvpairs.Key')),
            ],
            options={
                'verbose_name': 'Key-value pair',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='keyvaluepair',
            unique_together=set([('key', 'ref_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='key',
            unique_together=set([('model_ct', 'name')]),
        ),
    ]
