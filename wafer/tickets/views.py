import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView

from wafer.tickets.models import Ticket, TicketType
from wafer.tickets.forms import TicketForm

log = logging.getLogger(__name__)


class ClaimView(LoginRequiredMixin, FormView):
    template_name = 'wafer.tickets/claim.html'
    form_class = TicketForm

    def get_context_data(self, **kwargs):
        context = super(ClaimView, self).get_context_data(**kwargs)
        context['can_claim'] = self.can_claim()
        return context

    def can_claim(self):
        if settings.WAFER_REGISTRATION_MODE != 'ticket':
            raise Http404('Ticket-based registration is not in use')
        if not settings.WAFER_REGISTRATION_OPEN:
            return False
        return not self.request.user.userprofile.is_registered()

    def form_valid(self, form):
        if not self.can_claim():
            raise ValidationError('User may not claim a ticket')
        ticket = Ticket.objects.get(barcode=form.cleaned_data['barcode'])
        ticket.user = self.request.user
        ticket.save()
        return super(ClaimView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'wafer_user_profile', args=(self.request.user.username,))


# We assume that the system is using quicket's Zapier integration, turning
# Quicket events into web posts via the Zapier webhook endpoint.
# For Zapier, we assume a shared secret has been set in the X-Zapier-Secret
# header
@csrf_exempt
@require_POST
def zapier_cancel_hook(request):
    '''
    Zapier can post something like this when tickets are cancelled
    {
        "ticket_type": "Individual (Regular)",
        "barcode": "12345678",
        "email": "demo@example.com"
    }
    '''
    if request.META.get('HTTP_X_ZAPIER_SECRET', None) != settings.WAFER_TICKETS_SECRET:
        raise PermissionDenied('Incorrect secret')

    # This is required for python 3, and in theory fine on python 2
    payload = json.loads(request.body.decode('utf8'))
    ticket = Ticket.objects.filter(barcode=payload['barcode'])
    if ticket.exists():
        # delete the ticket
        ticket.delete()
    return HttpResponse("Cancelled\n", content_type='text/plain')


# We assume this is connected to the Quicket's 'guest added' Zapier
# event.
# Same considerations about the secret apply
@csrf_exempt
@require_POST
def zapier_guest_hook(request):
    '''
    Zapier can POST something like this when tickets are bought:
    {

        "ticket_type": "Individual (Regular)",
        "barcode": "12345678",
        "email": "demo@example.com"
    }
    '''
    if request.META.get('HTTP_X_ZAPIER_SECRET', None) != settings.WAFER_TICKETS_SECRET:
        raise PermissionDenied('Incorrect secret')

    # This is required for python 3, and in theory fine on python 2
    payload = json.loads(request.body.decode('utf8'))
    import_ticket(payload['barcode'], payload['ticket_type'],
                  payload['email'])

    return HttpResponse("Noted\n", content_type='text/plain')


def import_ticket(ticket_barcode, ticket_type, email):
    if Ticket.objects.filter(barcode=ticket_barcode).exists():
        log.debug('Ticket already registered: %s', ticket_barcode)
        return

    # truncate long ticket type names to length allowed by database
    ticket_type = ticket_type[:TicketType.MAX_NAME_LENGTH]
    type_, created = TicketType.objects.get_or_create(name=ticket_type)

    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(email=email, ticket=None)
    except UserModel.DoesNotExist:
        user = None
    except UserModel.MultipleObjectsReturned:
        # We're can't uniquely identify the user to associate this ticket
        # with, so leave it for them to figure out via the 'claim ticket'
        # interface
        user = None

    ticket = Ticket.objects.create(
        barcode=ticket_barcode,
        email=email,
        type=type_,
        user=user,
    )
    ticket.save()

    if user:
        log.info('Ticket registered: %s and linked to user', ticket)
    else:
        log.info('Ticket registered: %s. Unclaimed', ticket)
