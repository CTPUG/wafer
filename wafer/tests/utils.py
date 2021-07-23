"""Utilities for testing wafer."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


def create_user(username, email=None, superuser=False, perms=()):
    if superuser:
        create = get_user_model().objects.create_superuser
    else:
        create = get_user_model().objects.create_user
    if email is None:
        email = "%s@example.com" % username
    user = create(username, email, "%s_password" % username)
    for codename in perms:
        perm = Permission.objects.get(codename=codename)
        user.user_permissions.add(perm)
    if perms:
        user = get_user_model().objects.get(pk=user.pk)
    return user


def mock_avatar_url(self):
    """Avoid libravatar DNS lookups during tests"""
    if self.user.email is None:
        return None
    return "avatar-%s" % self.user.email
