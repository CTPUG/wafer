from django.contrib import admin
from django import forms

from wafer.schedule.models import Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED

class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(status=ACCEPTED)


class ScheduleItemAdmin(admin.ModelAdmin):
    form = ScheduleItemAdminForm


admin.site.register(Slot)
admin.site.register(Venue)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
