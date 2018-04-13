from django import template
from django.utils.html import format_html
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag()
def reviewed_badge(user, talk):
    """Returns a badge for the user's reviews of the talk"""
    if user.is_anonymous():
        return ''
    review = talk.reviews.filter(reviewer=user).first()
    if not review:
        return ''
    if review.is_current():
        return format_html(
            '<span class="badge badge-success" title="{}">R</span>',
            _('Reviewed'))
    else:
        return format_html(
            '<span class="badge badge-info" title="{}">O</span>',
            _('Reviewed, but outdated (modified since last review)'))
