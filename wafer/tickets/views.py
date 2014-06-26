import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from wafer.tickets.models import Ticket, TicketType
from wafer.tickets.forms import TicketForm


def claim(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = Ticket.objects.get(barcode=form.cleaned_data['barcode'])
            ticket.user = request.user
            ticket.save()
            return HttpResponseRedirect(reverse('wafer_user_profile',
                                                args=(request.user.username,)))
    else:
        form = TicketForm()

    context = {
        'form': form,
    }
    return render_to_response('wafer.tickets/claim.html', context,
                              context_instance=RequestContext(request))


@csrf_exempt
@require_POST
def quicket_hook(request):
    '''
    Quicket.co.za can POST something like this when tickets are bought:
    {
      "reference": "REF00123456",
      "event_id": 123,
      "event_name": "My Big Event",
      "amount": 0.00,
      "email": "demo@example.com",
      "action": "checkout_started",
      // Options are "checkout_started","checkout_cancelled","eft_pending",
      //             "checkout_completed"
      "tickets": [
        {
          "id": 122,
          "attendee_name": "",
          "attendee_email": "",
          "ticket_type": "Free Ticket",
          "price": 0.00,
          "barcode": 12345,
        },
        ...
      ],
    }
    '''
    if request.GET.get('secret') != settings.WAFER_TICKETS_SECRET:
        raise PermissionDenied('Incorrect secret')

    payload = json.load(request)
    for ticket in payload['tickets']:
        import_ticket(ticket['barcode'], ticket['ticket_type'],
                      ticket['attendee_email'])

    return HttpResponse("Noted\n", content_type='text/plain')


def import_ticket(ticket_barcode, ticket_type, email):
    if Ticket.objects.filter(barcode=ticket_barcode).exists():
        return

    type_, created = TicketType.objects.get_or_create(name=ticket_type)

    try:
        user = User.objects.get(email=email, ticket=None)
    except User.DoesNotExist:
        user = None

    ticket = Ticket.objects.create(
        barcode=ticket_barcode,
        email=email,
        type=type_,
        user=user,
    )
    ticket.save()
