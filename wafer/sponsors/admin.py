from django.contrib import admin

from wafer.sponsors.models import (File, SponsorshipPackage, Sponsor,
                                   TaggedFile)

from reversion.admin import VersionAdmin


class SponsorTaggedFileInline(admin.TabularInline):
    model = TaggedFile


class SponsorAdmin(VersionAdmin):
    inlines = (SponsorTaggedFileInline,)


class SponsorshipPackageAdmin(VersionAdmin):
    pass


admin.site.register(SponsorshipPackage, SponsorshipPackageAdmin)
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(File)
