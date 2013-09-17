from django.views.generic.list import ListView

from wafer.sponsors.models import Sponsor, SponsorshipPackage


class ShowSponsors(ListView):
    template_name = 'wafer.sponsors/sponsors.html'
    model = Sponsor

    def get_queryset(self):
        packages = SponsorshipPackage.objects.all()
        package_order = dict((p.pk, i) for i, p in enumerate(packages))

        def sponsor_key(sponsor):
            order = min(package_order[p.pk] for p in sponsor.packages)
            return (order, sponsor.name)

        sponsors = list(Sponsor.objects.all())
        sponsors.sort(key=sponsor_key)
        return sponsors


class ShowPackages(ListView):
    template_name = 'wafer.sponsors/packages.html'
    model = SponsorshipPackage
