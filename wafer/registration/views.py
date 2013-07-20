from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def redirect_profile(request):
    '''
    The default destination from logging in, redirect to the actual profile URL
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('wafer_user_profile',
                                            args=(request.user.username,)))
    else:
        return HttpResponseRedirect(reverse('wafer_page', args=('index',)))
