from django.core.exceptions import ValidationError


def validate_username(username):
    """Some usernames lead to problematic URLs and static file names"""
    if username.startswith('.'):
        raise ValidationError('usernames cannot start with a "."')
    if username in ('index.html', 'page'):
        raise ValidationError('This username is not available')
