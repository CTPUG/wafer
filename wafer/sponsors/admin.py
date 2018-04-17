from django.contrib import admin

from wafer.sponsors.models import File, SponsorshipPackage, Sponsor

from reversion.admin import VersionAdmin

class SponsorAdmin(VersionAdmin):
    pass


class SponsorshipPackageAdmin(VersionAdmin):
    pass


admin.site.register(SponsorshipPackage, SponsorshipPackageAdmin)
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(File)
