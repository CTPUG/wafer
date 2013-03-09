'''
Created on 29 Jun 2012

@author: euan
'''
from django.views import generic as generic_views
from django.contrib import messages

from wafer.models import WAITING_LIST_ON


class RegisterView(generic_views.CreateView):
    def dispatch(self, request, *args, **kwargs):
        if WAITING_LIST_ON:
            messages.warning(request, "PyConZA is currently fully booked. "
                             "Register below to be added to the waiting list "
                             "and we'll contact you as places become "
                             "available.")
        return super(RegisterView, self).dispatch(request, *args, **kwargs)


def contact(request):
    raise NotImplementedError()
