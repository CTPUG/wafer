from django.contrib import admin

from wafer.talks.models import Talk


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'corresponding_author', 'status')
    list_editable = ('status',)


admin.site.register(Talk, TalkAdmin)
