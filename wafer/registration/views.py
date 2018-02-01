from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from wafer.registration.sso import SSOError, debian_sso, github_sso


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
        return HttpResponseRedirect(
            'https://github.com/login/oauth/authorize?' + urlencode({
                'client_id': settings.WAFER_GITHUB_CLIENT_ID,
                'redirect_uri': request.build_absolute_uri(
                    reverse(github_login)),
                'scope': 'user:email',
                'state': request.META['CSRF_COOKIE'],
            }))

    try:
        if request.GET['state'] != request.META['CSRF_COOKIE']:
            raise SSOError('Incorrect state')

        user = github_sso(request.GET['code'])
    except SSOError as e:
        messages.error(request, u'%s' % e)
        return HttpResponseRedirect(reverse('auth_login'))

    login(request, user)

    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return redirect_profile(request)


def debian_login(request):
    if 'debian' not in settings.WAFER_SSO:
        raise Http404()

    try:
        user = debian_sso(request.META)
    except SSOError as e:
        messages.error(request, u'%s' % e)
        return HttpResponseRedirect(reverse('auth_login'))

    login(request, user)

    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return redirect_profile(request)
