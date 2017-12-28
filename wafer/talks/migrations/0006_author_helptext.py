# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0005_add_kv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='authors',
            field=models.ManyToManyField(
                help_text='The speakers presenting the talk.',
                related_name='talks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='talk',
            name='corresponding_author',
            field=models.ForeignKey(
                related_name='contact_talks', to=settings.AUTH_USER_MODEL,
                help_text='The person submitting the talk (and who questions '
                          'regarding the talk should be addressed to).',
                on_delete=models.CASCADE),
        ),
    ]
