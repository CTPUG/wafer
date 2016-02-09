from django.views.generic.list import ListView
from django.views.generic import DetailView

from rest_framework import viewsets

from wafer.sponsors.models import Sponsor, SponsorshipPackage
from wafer.sponsors.serializers import SponsorSerializer, PackageSerializer


class ShowSponsors(ListView):
    template_name = 'wafer.sponsors/sponsors.html'
    model = Sponsor

    def get_queryset(self):
        return Sponsor.objects.all().order_by('packages')


class SponsorView(DetailView):
    template_name = 'wafer.sponsors/sponsor.html'
    model = Sponsor


class ShowPackages(ListView):
    template_name = 'wafer.sponsors/packages.html'
    model = SponsorshipPackage


class SponsorViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer


class PackageViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = SponsorshipPackage.objects.all()
    serializer_class = PackageSerializer
