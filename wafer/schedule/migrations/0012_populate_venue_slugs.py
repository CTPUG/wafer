# Manual migration to populate Venue.slug for existing venues, using the
# same name-based value that DebConf used to derive stream URLs from the
# venue name, so those URLs don't change after upgrading.

import re

from django.db import migrations

def populate_slugs(apps, schema_editor):
    Venue = apps.get_model('schedule', 'Venue')
    for venue in Venue.objects.filter(slug=''):
        venue.slug = re.sub(r"[^a-z0-9-]+", "-", venue.name.lower())[:50]
        venue.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0011_venue_slug')
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]