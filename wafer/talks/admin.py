from django.contrib import admin

from wafer.talks.models import TalkType, Talk, TalkUrl

class TalkUrlInline(admin.TabularInline):
    model = TalkUrl


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author_name', 'get_author_contact',
                    'talk_type', 'get_in_schedule', 'status')
    list_editable = ('status',)

    inlines = [
              TalkUrlInline,
              ]


admin.site.register(Talk, TalkAdmin)
admin.site.register(TalkType)
admin.site.register(TalkUrl)
