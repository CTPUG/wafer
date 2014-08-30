import urllib
import logging

from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden

import requests

from wafer.users.models import UserProfile

log = logging.getLogger(__name__)


def redirect_profile(request):
    '''
    The default destination from logging in, redirect to the actual profile URL
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('wafer_user_profile',
                                            args=(request.user.username,)))
    else:
        return HttpResponseRedirect(reverse('wafer_page', args=('index',)))


def github_login(request):
    if 'code' not in request.GET:
        return HttpResponseRedirect(
            'https://github.com/login/oauth/authorize?' + urllib.urlencode({
                'client_id': settings.WAFER_GITHUB_CLIENT_ID,
                'redirect_uri': request.build_absolute_uri(
                    reverse(github_login)),
                'scope': 'user:email',
                'state': request.META['CSRF_COOKIE'],
            }))

    if request.GET['state'] != request.META['CSRF_COOKIE']:
        return HttpResponseForbidden('Incorrect state',
                                     content_type='text/plain')
    code = request.GET['code']

    r = requests.post('https://github.com/login/oauth/access_token', data={
        'client_id': settings.WAFER_GITHUB_CLIENT_ID,
        'client_secret': settings.WAFER_GITHUB_CLIENT_SECRET,
        'code': code,
    })
    if r.status_code != 200:
        return HttpResponseForbidden('Invalid code', content_type='text/plain')
    token = r.content

    r = requests.get('https://api.github.com/user?%s' % token)
    if r.status_code != 200:
        return HttpResponseForbidden('Unexpected response from github',
                content_type='text/plain')
    gh = r.json()

    email = gh.get('email', None)
    if not email:  # No public e-mail address
        r = requests.get('https://api.github.com/user/emails?%s' % token)
        if r.status_code != 200:
            return HttpResponseForbidden('Failed to obtain email address from'
                    ' github - unexpected response', content_type='text/plain')
        try:
            email = r.json()[0]['email']
        except (KeyError, IndexError) as e:
            log.debug('Error extracting github email address: %s', e)
            return HttpResponseForbidden('Failed to obtain email address from'
                    ' github - unexpected response', content_type='text/plain')

    try:
        user = authenticate(github_login=gh['login'], name=gh['name'], email=email,
                            blog=gh['blog'])
    except KeyError as e:
        log.debug('Error creating account from github information: %s', e)
        return HttpResponseForbidden('Unexpected response from github.'
                ' Authentication failed', content_type='text/plain')
    except UserProfile.MultipleObjectsReturned as e:
        # FIXME: This is a short term workaround. Find a better fix
        # later
        log.debug('Duplicate accounts for github login %s: %s',
                  gh['login'], e)
        return HttpResponseForbidden('Multiple accounts associated with'
                ' these github credentials. Authentication failed',
                content_type='text/plain')

    if not user:
        return HttpResponseForbidden('Authentication with github credentials'
                ' failed', content_type='text/plain')
    login(request, user)
    return HttpResponseRedirect(reverse(redirect_profile))
