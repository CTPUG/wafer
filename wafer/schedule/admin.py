from django.contrib import admin
from django import forms

from wafer.schedule.models import Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page

class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(status=ACCEPTED)
        # We assume items not in the menu aren't intended for the schedule
        # either - Is this the best assumption?
        self.fields['page'].queryset = Page.objects.filter(
            include_in_menu=True)


class ScheduleItemAdmin(admin.ModelAdmin):
    form = ScheduleItemAdminForm

    change_list_template = 'admin/scheduleitem_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super(ScheduleItemAdmin, self).changelist_view(request,
                                                              extra_context)


class SlotAdminForm(forms.ModelForm):
    class Meta:
        model = Slot

    class Media:
        js = ('js/scheduledatetime.js',)


class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm

    list_display = ('__unicode__', 'end_time')
    list_editable = ('end_time',)


admin.site.register(Slot, SlotAdmin)
admin.site.register(Venue)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
