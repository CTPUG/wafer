from django.contrib import admin

from wafer.sponsors.models import File, SponsorshipPackage, Sponsor


admin.site.register(SponsorshipPackage)
admin.site.register(Sponsor)
admin.site.register(File)
