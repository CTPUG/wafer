from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden

import requests


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
    assert r.status_code == 200
    gh = r.json()

    email = gh['email']
    if not email:  # No public e-mail address
        r = requests.get('https://api.github.com/user/emails?%s' % token)
        assert r.status_code == 200
        email = r.json()[0]

    user = authenticate(github_login=gh['login'], name=gh['name'], email=email,
                        blog=gh['blog'])
    assert user
    login(request, user)
    return HttpResponseRedirect(reverse(redirect_profile))
