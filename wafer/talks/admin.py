from django.contrib import admin

from wafer.talks.models import Talk


class TalkAdmin(admin.ModelAdmin):
    list_display = ('corresponding_author', 'title', 'status')


admin.site.register(Talk, TalkAdmin)
