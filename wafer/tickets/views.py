import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from wafer.tickets.models import Ticket, TicketType


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
        type=type_,
        user=user,
    )
    ticket.save()
