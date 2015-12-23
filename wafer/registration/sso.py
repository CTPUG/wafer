# coding: utf-8

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError

import requests

MAX_APPEND = 20

log = logging.getLogger(__name__)


class SSOError(Exception):
    pass


def sso(identifier, desired_username, name, email, profile_fields=None):
    """
    Look up a user that has been authenticated against the filter params
    `identifier`. If necessary, create one, using the remaining parameters.
    """
    try:
        user = get_user_model().objects.get(**identifier)
    except ObjectDoesNotExist:
        user = _create_desired_user(desired_username)
        _configure_user(user, name, email, profile_fields)
    except MultipleObjectsReturned:
        log.warning('Multiple accounts match %r', identifier)
        raise SSOError('Multiple accounts match %r' % identifier)

    if not user.is_active:
        raise SSOError('Account disabled')

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
    log.warning('Ran out of possible usernames for %s', desired_username)
    raise SSOError('Ran out of possible usernames for %s' % desired_username)


def _configure_user(user, name, email, profile_fields):
    if name:
        user.first_name, user.last_name = name

    for attr in ('first_name', 'last_name'):
        max_length = get_user_model()._meta.get_field(attr).max_length
        if len(getattr(user, attr)) > max_length:
            setattr(user, attr, getattr(user, attr)[:max_length - 1] + u'…')

    user.email = email
    user.save()

    profile = user.userprofile
    if profile_fields:
        for k, v in profile_fields.iteritems():
            setattr(profile, k, v)
    profile.save()


def github_sso(code):
    r = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': settings.WAFER_GITHUB_CLIENT_ID,
        'client_secret': settings.WAFER_GITHUB_CLIENT_SECRET,
        'code': code,
    })
    if r.status_code != 200:
        log.warning('Response %s from api.github.com', r.status_code)
        raise SSOError('Invalid code')
    token = r.content

    r = requests.get('https://api.github.com/user?%s' % token)
    if r.status_code != 200:
        log.warning('Response %s from api.github.com', r.status_code)
        raise SSOError('Failed response from GitHub')
    gh = r.json()

    try:
        login = gh['login']
        name = gh['name'].partition(' ')[::2]
    except KeyError as e:
        log.warning('Error creating account from github information: %s', e)
        raise SSOError('GitHub profile missing required content')

    email = gh.get('email', None)
    if not email:  # No public e-mail address
        r = requests.get('https://api.github.com/user/emails?%s' % token)
        if r.status_code != 200:
            log.warning('Response %s from api.github.com', r.status_code)
            raise SSOError('Failed response from GitHub')
        try:
            email = r.json()[0]['email']
        except (KeyError, IndexError) as e:
            log.warning('Error extracting github email address: %s', e)
            raise SSOError('Failed to obtain email address from GitHub')

    profile_fields = {
        'github_username': login,
    }
    if 'blog' in gh:
        profile_fields['blog'] = gh['blog']

    user = sso(
        identifier={'userprofile__github_username': login},
        desired_username=login, name=name, email=email,
        profile_fields=profile_fields)
    return user


def debian_sso(meta):
    authentication_status = meta.get('SSL_CLIENT_VERIFY', None)
    if authentication_status != "SUCCESS":
        raise SSOError('Requires authentication via Client Certificate')

    email = meta['SSL_CLIENT_S_DN_CN']
    identifier = {'email': email}
    username = email.split('@', 1)[0]

    name = ('Unknown User', email)
    if not get_user_model().objects.filter(**identifier).exists():
        r = requests.get('https://nm.debian.org/api/people',
                         params={'uid': username},
                         headers={'Api-Key': settings.WAFER_DEBIAN_NM_API_KEY})
        if r.status_code != 200:
            log.warning('Response %s from nm.debian.org', r.status_code)
            raise SSOError('Failed to query nm.debian.org')
        if 'r' not in r.json():
            log.warning('Error parsing nm.debian.org response: %r', r.json())
            raise SSOError('Failed to parse nm.debian.org respnose')
        # The API performs substring queries, so we need to find the correct
        # entry in the response.
        for person in r.json()['r']:
            if person['uid'] == username:
                first_name = person['cn']
                if person['mn']:
                    first_name += u' ' + person['mn']
                last_name = person['sn']
                name = (first_name, last_name)
                break

    user = sso(identifier=identifier, desired_username=username, name=name,
               email=email)
    return user
