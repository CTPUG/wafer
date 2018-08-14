from django import template

register = template.Library()


@register.inclusion_tag('wafer.talks/reviewed-badge.html')
def reviewed_badge(user, talk):
    """Returns a badge for the user's reviews of the talk"""
    context = {
        'reviewed': False,
    }

    review = None
    if user and not user.is_anonymous():
        review = talk.reviews.filter(reviewer=user).first()

    if review:
        context['reviewed'] = True
        context['review_is_current'] = review.is_current()

    return context
