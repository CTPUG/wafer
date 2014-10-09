from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from wafer.talks.models import TalkType, Talk, TalkUrl

class ScheduleListFilter(admin.SimpleListFilter):
    title = _('in schedule')
    parameter_name = 'schedule'

    def lookups(self, request, model_admin):
        return (
            ('in', _('Allocated to schedule')),
            ('out', _('Not allocated')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'in':
            return queryset.filter(scheduleitem__isnull=False)
        elif self.value() == 'out':
            return queryset.filter(scheduleitem__isnull=True)
        return queryset

class TalkUrlAdmin(admin.ModelAdmin):
    list_display = ('description', 'talk', 'url')

class TalkUrlInline(admin.TabularInline):
    model = TalkUrl


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author_name', 'get_author_contact',
                    'talk_type', 'get_in_schedule', 'has_url', 'status')
    list_editable = ('status',)
    list_filter = ('status', 'talk_type', ScheduleListFilter)

    inlines = [
              TalkUrlInline,
              ]


admin.site.register(Talk, TalkAdmin)
admin.site.register(TalkType)
admin.site.register(TalkUrl, TalkUrlAdmin)
