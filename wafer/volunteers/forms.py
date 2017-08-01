from datetime import datetime, timedelta

from django import forms
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, HTML, Submit

from wafer.schedule.models import ScheduleItem, Venue
from wafer.volunteers.models import Task, TaskTemplate, TaskLocation


class VideoMassCreateTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        video_tasks = TaskTemplate.objects.filter(video_task=True)
        schedule_items = list(
            ScheduleItem.objects.filter(talk__video=True,
                                        venue__tasklocation__isnull=False)
                                .all()
        )
        venues = Venue.objects.filter(tasklocation__isnull=False).all()
        schedule_items.sort(key=lambda si: si.get_start_time())

        venue_divs = {venue.pk: Div(HTML('<h3>%s</h3>' % venue.name),
                                    css_class='venue-%s' % venue.pk)
                      for venue in venues}
        for schedule_item in schedule_items:
            tasks_for_item = Fieldset(legend='%s - %s - %s' % (
                schedule_item.venue.name,
                schedule_item.get_start_time(),
                schedule_item.talk.title,
            ))
            for task in video_tasks:
                fieldname = '%s:%s' % (schedule_item.pk, task.pk)
                self.fields[fieldname] = forms.BooleanField(required=False,
                                                            label=task.name)
                tasks_for_item.append(fieldname)
            venue_divs[schedule_item.venue.pk].append(tasks_for_item)

        self.helper = FormHelper()
        self.helper.layout = Layout(*venue_divs.values())
        self.helper.add_input(Submit('submit', 'Create Tasks'))

    def clean(self):
        tz = timezone.get_default_timezone()
        cleaned_data = super().clean()
        new_data = {}
        for pks, create_task in cleaned_data.items():
            schedule_item_pk, task_template_pk = map(int, pks.split(':'))
            si = ScheduleItem.objects.get(pk=schedule_item_pk)
            template = TaskTemplate.objects.get(pk=task_template_pk)

            start = timezone.make_aware(datetime.strptime(
                si.get_start_time(), "%b %d (%a), %H:%M"
            ).replace(year=2017), tz)

            end = start + timedelta(minutes=si.get_duration_minutes())

            task_data = {
                'start': start,
                'end': end,
                'location': TaskLocation.objects.get(venue=si.venue),
            }

            if create_task:
                task = Task.objects.get_or_create(talk=si.talk,
                                                  template=template,
                                                  defaults=task_data)
                new_data[(si, template)] = task
            else:
                Task.objects.filter(talk=si.talk, template=template,).delete()
                new_data[(si, template)] = None
        cleaned_data.update(new_data)
        return cleaned_data
