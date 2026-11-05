import os

from django.core.files.base import ContentFile
from django.db import migrations


def remove_legacy_public_files(apps, schema_editor):
    Talk = apps.get_model('talks', 'Talk')
    TalkFile = apps.get_model('talks', 'TalkFile')
    database = schema_editor.connection.alias

    for talk in Talk.objects.using(database).exclude(
        presentation=''
    ).iterator():

        old_file = talk.presentation

        if not old_file or not old_file.name:
            continue

        filename = os.path.basename(old_file.name)

        attachment = TalkFile.objects.using(database).filter(
            talk_id=talk.pk,
            name=filename,
            item__startswith='talk_files/legacy/',
        ).first()

        if attachment is None:
            raise RuntimeError(
                f"Talk {talk.pk}: private replacement for "
                f"{old_file.name} was not found. "
                "The public file has been preserved."
            )

        if not attachment.item.storage.exists(attachment.item.name):
            raise RuntimeError(
                f"Talk {talk.pk}: private replacement "
                f"{attachment.item.name} is missing. "
                "The public file has been preserved."
            )

        if old_file.storage.exists(old_file.name):
            old_file.storage.delete(old_file.name)


def restore_legacy_public_files(apps, schema_editor):
    Talk = apps.get_model('talks', 'Talk')
    TalkFile = apps.get_model('talks', 'TalkFile')
    database = schema_editor.connection.alias

    for talk in Talk.objects.using(database).iterator():

        attachment = TalkFile.objects.using(database).filter(
            talk_id=talk.pk,
            item__startswith='talk_files/legacy/',
        ).first()

        if attachment is None:
            continue

        if not attachment.item.storage.exists(attachment.item.name):
            raise RuntimeError(
                f"Cannot restore presentation for talk {talk.pk}: "
                "private attachment is missing."
            )

        filename = os.path.basename(attachment.item.name)

        with attachment.item.storage.open(
            attachment.item.name, 'rb'
        ) as source:
            talk.presentation.save(
                filename,
                ContentFile(source.read()),
                save=False,
            )

        talk.save(using=database)


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0028_migrate_legacy_presentation'),
    ]

    operations = [
        migrations.RunPython(
            remove_legacy_public_files,
            restore_legacy_public_files,
        ),
        migrations.RemoveField(
            model_name='talk',
            name='presentation',
        ),
    ]
