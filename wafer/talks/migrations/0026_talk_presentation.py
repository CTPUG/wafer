from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('talks', '0025_talk_num_schedulable'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='presentation',
            field=models.FileField(
                blank=True,
                help_text=_('PDF or ZIP presentation file.'),
                null=True,
                upload_to='talk_presentations/',
                verbose_name=_('presentation'),
            ),
        ),
    ]
