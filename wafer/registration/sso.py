# coding: utf-8

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError

import requests

from wafer.kv.models import KeyValue

MAX_APPEND = 20

log = logging.getLogger(__name__)


class SSOError(Exception):
    pass


def sso(user, desired_username, name, email, profile_fields=None):
    """
    Create a user, if the provided `user` is None, from the parameters.
    Then log the user in, and return it.
    """
    if not user:
        if not getattr(settings, 'REGISTRATION_OPEN', True):
            raise SSOError('Account registration is closed')

        if get_user_model().objects.filter(email=email).exists():
            raise SSOError(
                "An account already exists for {} that doesn't use SSO. "
                "Refusing to create a second account.".format(email))
        user = _create_desired_user(desired_username)
        _configure_user(user, name, email, profile_fields)

    if not user.is_active:
        raise SSOError('Account disabled')

    # login() expects the logging in backend to be set on the user.
    # We are bypassing login, so fake it.
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    return user


def _create_desired_user(desired_username):
    for append in range(MAX_APPEND):
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
        for k, v in profile_fields.items():
            setattr(profile, k, v)
    profile.save()


def _check_count(kv_search):
    """Return the number of matches found.

       We need to check for two possible sources of duplicates which
       will make us unable to uniquely identify the user:
         1) Multiple different KeyValues created with the same value
         2) Multiple user profiles assigned to the same KeyValue
       Both errors should require something strange to have happened - importing data
       into an existing database, weird API interactions, etc -, but we
       don't want to allow incorrect access to an existing account.
       """
    if kv_search.count() > 1:
        # Multiple KeyValues
        return kv_search.count()
    if kv_search.count() == 1:
        # Could have multiple user profiles
        # Will be 1 in the case of a unique match, which is what we want
        return kv_search[0].userprofile_set.count()
    # No matches
    return 0


def github_sso(code):
    r = requests.post(
        'https://github.com/login/oauth/access_token', data={
            'client_id': settings.WAFER_GITHUB_CLIENT_ID,
            'client_secret': settings.WAFER_GITHUB_CLIENT_SECRET,
            'code': code,
        }, headers={
            'Accept': 'application/json',
        })
    if r.status_code != 200:
        log.warning('Response %s from api.github.com', r.status_code)
        raise SSOError('Invalid code')
    token = r.json()['access_token']
    auth_headers = {'Authorization': 'token {}'.format(token)}

    r = requests.get('https://api.github.com/user', headers=auth_headers)
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
        r = requests.get(
            'https://api.github.com/user/emails', headers=auth_headers)
        if r.status_code != 200:
            log.warning('Response %s from api.github.com', r.status_code)
            raise SSOError('Failed response from GitHub')
        try:
            email = r.json()[0]['email']
        except (KeyError, IndexError) as e:
            log.warning('Error extracting github email address: %s', e)
            raise SSOError('Failed to obtain email address from GitHub')

    # TODO: Extend this to also set the github profile url KV
    profile_fields = {}
    if 'blog' in gh:
        profile_fields['blog'] = gh['blog']

    group = Group.objects.get_by_natural_key('Registration')
    user = None

    kv_search = KeyValue.objects.filter(
            group=group, key='github_sso_account_id', value=login,
            userprofile__isnull=False)
    count = _check_count(kv_search)
    if count > 1:
        message = 'Multiple accounts have the same GitHub SSO id: %s'
        log.warning(message, login)
        raise SSOError(message % login)

    if count:
        user = kv_search[0].userprofile_set.first().user

    user = sso(user=user, desired_username=login, name=name, email=email,
               profile_fields=profile_fields)
    user.userprofile.kv.get_or_create(group=group, key='github_sso_account_id',
                                      defaults={'value': login})
    return user


def gitlab_sso(code, redirect_uri):
    host = getattr(settings, 'WAFER_GITLAB_HOSTNAME', 'gitlab.com')
    r = requests.post(
        'https://{}/oauth/token'.format(host),
        data={
            'client_id': settings.WAFER_GITLAB_CLIENT_ID,
            'client_secret': settings.WAFER_GITLAB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
    if r.status_code != 200:
        log.warning('Response %s from %s', r.status_code, host)
        raise SSOError('Invalid code')
    token = r.json()['access_token']
    auth_headers = {'Authorization': 'Bearer {}'.format(token)}

    r = requests.get(
        'https://{}/api/v4/user'.format(host), headers=auth_headers)
    if r.status_code != 200:
        log.warning('Response %s from GitLab API', r.status_code)
        raise SSOError('Failed response from GitLab')
    gl = r.json()

    try:
        username = gl['username']
        name = gl['name'].partition(' ')[::2]
        email = gl['email']
    except KeyError as e:
        log.warning('Error creating account from gitlab information: %s', e)
        raise SSOError('GitLab profile missing required content')

    group = Group.objects.get_by_natural_key('Registration')
    user = None
    kv_search = KeyValue.objects.filter(
            group=group, key='gitlab_sso_account_id', value=gl['id'],
            userprofile__isnull=False)

    count = _check_count(kv_search)
    if count > 1:
        message = 'Multiple accounts have GitLab SSOed for User ID %s'
        log.warning(message, gl['id'])
        raise SSOError(message % gl['id'])

    if count:
        user = kv_search[0].userprofile_set.first().user

    user = sso(user=user, desired_username=username, name=name, email=email)
    user.userprofile.kv.get_or_create(group=group, key='gitlab_sso_account_id',
                                      defaults={'value': gl['id']})
    return user
