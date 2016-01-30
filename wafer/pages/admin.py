from django.contrib import admin

from wafer.pages.models import File, Page

from reversion.admin import VersionAdmin


class PageAdmin(VersionAdmin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'get_people_display_names', 'get_in_schedule')


admin.site.register(Page, PageAdmin)
admin.site.register(File)
