from django.views.generic.list import ListView

from wafer.sponsors.models import Sponsor, SponsorshipPackage


class ShowSponsors(ListView):
    template_name = 'wafer.sponsors/sponsors.html'
    model = Sponsor

    def get_queryset(self):
        return Sponsor.objects.all().order_by('packages')


class ShowPackages(ListView):
    template_name = 'wafer.sponsors/packages.html'
    model = SponsorshipPackage
