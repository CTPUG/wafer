from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import constant_time_compare, get_random_string
from django.utils.http import urlencode

from wafer.registration.sso import SSOError, github_sso, gitlab_sso


def redirect_profile(request):
    '''
    The default destination from logging in, redirect to the actual profile URL
    '''
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('wafer_user_profile',
                                            args=(request.user.username,)))
    else:
        return redirect_to_login(next=reverse(redirect_profile))


def github_login(request):
    if 'github' not in settings.WAFER_SSO:
        raise Http404()

    if 'code' not in request.GET:
        oauth_state = get_random_string(length=32)
        request.session['oauth_state'] = oauth_state
        return HttpResponseRedirect(
            'https://github.com/login/oauth/authorize?' + urlencode({
                'client_id': settings.WAFER_GITHUB_CLIENT_ID,
                'redirect_uri': request.build_absolute_uri(
                    reverse(github_login)),
                'scope': 'user:email',
                'state': oauth_state,
            }))

    try:
        oauth_state = request.session.pop('oauth_state', '')
        if not constant_time_compare(request.GET['state'], oauth_state):
            raise SSOError('Incorrect state')

        user = github_sso(request.GET['code'])
    except SSOError as e:
        messages.error(request, u'%s' % e)
        return HttpResponseRedirect(reverse('auth_login'))

    login(request, user)

    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return redirect_profile(request)


def gitlab_login(request):
    if 'gitlab' not in settings.WAFER_SSO:
        raise Http404()

    redirect_uri = request.build_absolute_uri(reverse(gitlab_login))
    if 'code' not in request.GET:
        oauth_state = get_random_string(length=32)
        request.session['oauth_state'] = oauth_state
        return HttpResponseRedirect(
            'https://{}/oauth/authorize?'.format(
                getattr(settings, 'WAFER_GITLAB_HOSTNAME', 'gitlab.com'))
            + urlencode({
                'client_id': settings.WAFER_GITLAB_CLIENT_ID,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'read_user',
                'state': oauth_state,
            }))

    try:
        oauth_state = request.session.pop('oauth_state', '')
        if not constant_time_compare(request.GET['state'], oauth_state):
            raise SSOError('Incorrect state')

        user = gitlab_sso(request.GET['code'], redirect_uri)
    except SSOError as e:
        messages.error(request, u'%s' % e)
        return HttpResponseRedirect(reverse('auth_login'))

    login(request, user)

    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return redirect_profile(request)
