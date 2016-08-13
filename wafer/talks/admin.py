from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin
from easy_select2 import select2_modelform_meta

from wafer.compare.admin import CompareVersionAdmin, DateModifiedFilter
from wafer.talks.models import TalkType, Talk, TalkUrl, render_author


class AdminTalkForm(forms.ModelForm):

    Meta = select2_modelform_meta(Talk)

    def __init__(self, *args, **kwargs):
        super(AdminTalkForm, self).__init__(*args, **kwargs)
        self.fields['authors'].label_from_instance = render_author
        self.fields['corresponding_author'].label_from_instance = render_author


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


class TalkUrlAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('description', 'talk', 'url')


class TalkUrlInline(admin.TabularInline):
    model = TalkUrl


class TalkAdmin(CompareVersionAdmin, admin.ModelAdmin):
    list_display = ('title', 'get_corresponding_author_name',
                    'get_corresponding_author_contact', 'talk_type',
                    'get_in_schedule', 'has_url', 'status')
    list_editable = ('status',)
    list_filter = ('status', 'talk_type', ScheduleListFilter, DateModifiedFilter)
    exclude = ('kv',)

    inlines = [
        TalkUrlInline,
    ]
    form = AdminTalkForm


class TalkTypeAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('name', 'order', 'disable_submission', 'css_class')
    readonly_fields = ('css_class',)


admin.site.register(Talk, TalkAdmin)
admin.site.register(TalkType, TalkTypeAdmin)
admin.site.register(TalkUrl, TalkUrlAdmin)
