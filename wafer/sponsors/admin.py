from django.contrib import admin

from wafer.sponsors.models import File, SponsorshipPackage, Sponsor

from reversion.admin import VersionAdmin

class SponsorAdmin(VersionAdmin, admin.ModelAdmin):
    pass


class SponsorshipPackageAdmin(VersionAdmin, admin.ModelAdmin):
    pass


admin.site.register(SponsorshipPackage, SponsorshipPackageAdmin)
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(File)
