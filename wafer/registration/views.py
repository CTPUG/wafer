import urllib
import logging

from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden

import requests

from wafer.registration.sso import sso

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
        return HttpResponseForbidden(
            'Unexpected response from github', content_type='text/plain')
    gh = r.json()

    if 'login' not in gh or 'name' not in gh:
        log.debug('Error creating account from github information: %s', e)
        return HttpResponseForbidden(
            'Unexpected response from github. Authentication failed',
            content_type='text/plain')

    email = gh.get('email', None)
    if not email:  # No public e-mail address
        r = requests.get('https://api.github.com/user/emails?%s' % token)
        if r.status_code != 200:
            return HttpResponseForbidden(
                'Failed to obtain email address from github '
                '- unexpected response',
                content_type='text/plain')
        try:
            email = r.json()[0]['email']
        except (KeyError, IndexError) as e:
            log.debug('Error extracting github email address: %s', e)
            return HttpResponseForbidden(
                'Failed to obtain email address from github '
                '- unexpected response',
                content_type='text/plain')

    profile_fields = {
        'github_username': gh['login'],
    }
    if 'blog' in gh:
        profile_fields['blog'] = gh['blog']

    user = sso(
        identifier={'userprofile__github_username': gh['login']},
        desired_username=gh['login'], name=gh['name'], email=email,
        profile_fields=profile_fields)

    if not user:
        return HttpResponseForbidden(
            'Authentication with GitHub credentials failed',
            content_type='text/plain')

    if not user.is_active:
        return HttpResponseForbidden(
            'Account disabled', content_type='text/plain')

    login(request, user)

    return HttpResponseRedirect(reverse(redirect_profile))
