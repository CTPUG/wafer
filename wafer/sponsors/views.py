from django.views.generic.list import ListView
from django.views.generic import DetailView

from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from wafer.sponsors.models import Sponsor, SponsorshipPackage
from wafer.sponsors.serializers import SponsorSerializer, PackageSerializer


class ShowSponsors(ListView):
    template_name = 'wafer.sponsors/sponsors.html'
    model = Sponsor

    def get_queryset(self):
        return Sponsor.objects.all().order_by('packages', 'order', 'id')


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
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )


class PackageViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = SponsorshipPackage.objects.all()
    serializer_class = PackageSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
