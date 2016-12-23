from django import template

from wafer.sponsors.models import Sponsor, SponsorshipPackage

register = template.Library()


@register.inclusion_tag('wafer.sponsors/sponsors_block.html')
def sponsors():
    return {
        'sponsors': Sponsor.objects.all().order_by('packages'),
        'packages': SponsorshipPackage.objects.all().prefetch_related('files'),
    }


# We use assignment_tag for compatibility with Django 1.8
# Once we drop 1.8 support, we should change this to
# simple_tag
@register.assignment_tag(takes_context=True)
def sponsor_image_url(context, name):
    """Returns the corresponding url from the sponsors images"""
    sponsor = context['sponsor']
    if sponsor.files.filter(name=name).exists():
        # We avoid worrying about multiple matches by always
        # returning the first one.
        return sponsor.files.filter(name=name).first().item.url
    return ''
