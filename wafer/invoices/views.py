from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404

from wafer.conf_registration.models import RegisteredAttendee


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
