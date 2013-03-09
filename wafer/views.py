'''
Created on 29 Jun 2012

@author: euan
'''
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views import generic as generic_views
from django.contrib import messages

from pycon.models import AttendeeRegistration, WAITING_LIST_ON


class RegisterView(generic_views.CreateView):
    def dispatch(self, request, *args, **kwargs):
        if WAITING_LIST_ON:
            messages.warning(request, "PyConZA is currently fully booked. "
                             "Register below to be added to the waiting list "
                             "and we'll contact you as places become "
                             "available.")
        return super(RegisterView, self).dispatch(request, *args, **kwargs)


def attendee_invoice(request, invoice_id):
    """PDF invoice for the given account UID."""
    attendee = get_object_or_404(AttendeeRegistration, invoice_id=invoice_id)
    if attendee.registration_type is None or attendee.invoice_pdf is None:
        return HttpResponseNotFound("Invoice not found.",
                                    content_type="text/plain")

    filename, pdf_data = attendee.get_invoice_pdf()

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        filename.encode("utf-8"),)

    response.write(pdf_data)
    return response
