import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """. and .. lead to problematic URLs and static file names"""
    if re.match(r'^\.+$', username):
        raise ValidationError(
            "usernames cannot consist of only .")
    if username in ('index.html', 'page'):
        raise ValidationError('Not an acceptable username')
