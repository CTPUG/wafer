import os

from django.core.files.base import ContentFile
from django.db import migrations


def migrate_presentations(apps, schema_editor):
    Talk = apps.get_model('talks', 'Talk')
    TalkFile = apps.get_model('talks', 'TalkFile')
    database = schema_editor.connection.alias

    for talk in Talk.objects.using(database).exclude(
        presentation=''
    ).iterator():
        old_file = talk.presentation

        if not old_file or not old_file.name:
            continue

        if not old_file.storage.exists(old_file.name):
            continue

        filename = os.path.basename(old_file.name)

        with old_file.storage.open(old_file.name, 'rb') as source:
            attachment = TalkFile(
                talk_id=talk.pk,
                name=filename,
                description='',
                public=False,
            )
            attachment.item.save(
                'legacy/' + filename,
                ContentFile(source.read()),
                save=False,
            )
            attachment.save(using=database)


def reverse_migration(apps, schema_editor):
    TalkFile = apps.get_model('talks', 'TalkFile')
    database = schema_editor.connection.alias

    legacy_files = TalkFile.objects.using(database).filter(
        item__startswith='talk_files/legacy/'
    )

    for attachment in legacy_files.iterator():
        attachment.item.storage.delete(attachment.item.name)
        attachment.delete(using=database)


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0027_talkfile'),
    ]

    operations = [
        migrations.RunPython(
            migrate_presentations,
            reverse_migration,
        ),
    ]
