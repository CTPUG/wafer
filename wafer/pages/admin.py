from django.contrib import admin

from wafer.pages.models import File, Page


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'get_in_schedule')


admin.site.register(Page, PageAdmin)
admin.site.register(File)
