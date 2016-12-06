# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0004_auto_20160813_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsorshippackage',
            name='symbol',
            field=models.CharField(blank=True, help_text='Optional symbol to display in the sponsors list next to sponsors who have sponsored at this list, (for example *).', max_length=1),
        ),
    ]
