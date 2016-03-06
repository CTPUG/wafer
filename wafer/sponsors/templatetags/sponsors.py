from django import template

from wafer.sponsors.models import Sponsor, SponsorshipPackage

register = template.Library()


@register.inclusion_tag('wafer.sponsors/sponsors_block.html')
def sponsors():
    return {
        'sponsors': Sponsor.objects.all().order_by('packages'),
        'packages': SponsorshipPackage.objects.all().prefetch_related('files'),
    }
