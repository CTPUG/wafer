from django.contrib import admin

from wafer.schedule.models import Venue, Slot, ScheduleItem


admin.site.register(Slot)
admin.site.register(Venue)
admin.site.register(ScheduleItem)
