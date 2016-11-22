# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


# Data migration for the changed talk status

def change_pending(apps, schema_editor):
    # Change Pending (P) status to
    # (S) Submitted
    # Use apps to ensure we have the correct version
    Talk = apps.get_model("talks", "Talk")
    for talk in Talk.objects.filter(status='P'):
        talk.status = 'S'
        talk.save()


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0010_auto_20161121_2134'),
    ]

    operations = [
            migrations.RunPython(change_pending),
    ]
