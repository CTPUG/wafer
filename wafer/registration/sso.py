import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError

MAX_APPEND = 20

log = logging.getLogger(__name__)


def sso(identifier, desired_username, name, email, profile_fields):
    """
    Look up a user that has been authenticated against the filter params
    `identifier`. If necessary, create one, using the remaining parameters.
    """
    try:
        user = get_user_model().objects.get(**identifier)
    except ObjectDoesNotExist:
        user = _create_desired_user(desired_username)
        if user:
            _configure_user(user, name, email, profile_fields)
    except MultipleObjectsReturned:
        log.error('Multiple accounts match %r', identifier)
        return None

    # login() expects the logging in backend to be set on the user.
    # We are bypassing login, so fake it.
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    return user


def _create_desired_user(desired_username):
    for append in xrange(MAX_APPEND):
        username = desired_username
        if append:
            username += str(append)
        try:
            return get_user_model().objects.create(username=username)
        except IntegrityError:
            continue
    log.error('Ran out of possible usernames for %s', desired_username)


def _configure_user(user, name, email, profile_fields):
    if name:
        user.first_name, _,  user.last_name = name.partition(' ')
    user.email = email
    user.save()

    profile = user.userprofile
    for k, v in profile_fields.iteritems():
        setattr(profile, k, v)
    profile.save()
