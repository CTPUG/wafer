import django.db.models.deletion
import wafer.talks.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0026_talk_presentation'),
    ]

    operations = [
        migrations.CreateModel(
            name='TalkFile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                (
                    'item',
                    models.FileField(
                        storage=wafer.talks.storage.PrivateTalkStorage(),
                        upload_to='talk_files/',
                    ),
                ),
                (
                    'public',
                    models.BooleanField(
                        default=False,
                        help_text='Make this attachment publicly downloadable.',
                    ),
                ),
                (
                    'talk',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='attachments',
                        to='talks.talk',
                    ),
                ),
            ],
        ),
    ]
