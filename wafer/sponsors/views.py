from bakery.views import BuildableListView, BuildableDetailView
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from wafer.sponsors.models import Sponsor, SponsorshipPackage
from wafer.sponsors.serializers import SponsorSerializer, PackageSerializer


class ShowSponsors(BuildableListView):
    template_name = 'wafer.sponsors/sponsors.html'
    model = Sponsor
    build_path = 'sponsors/index.html'

    def get_queryset(self):
        return Sponsor.objects.all().order_by('packages', 'order', 'id')


class SponsorView(BuildableDetailView):
    template_name = 'wafer.sponsors/sponsor.html'
    model = Sponsor


class ShowPackages(BuildableListView):
    template_name = 'wafer.sponsors/packages.html'
    model = SponsorshipPackage
    build_path = 'sponsors/packages/index.html'


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
