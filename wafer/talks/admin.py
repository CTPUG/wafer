from django.contrib import admin

from wafer.talks.models import Talk


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author_name', 'get_author_contact',
                    'status')
    list_editable = ('status',)


admin.site.register(Talk, TalkAdmin)
