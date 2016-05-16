import json

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from wafer.tickets.views import import_ticket
from wafer.tickets.models import Ticket, TicketType


class ImportTicketTests(TestCase):
    def setUp(self):
        self.user_email = "user@example.com"

    def create_user(self, email, user_name="User Foo"):
        UserModel = get_user_model()
        return UserModel.objects.create_user(user_name, email=email)

    def test_simple_import_with_user(self):
        user = self.create_user(self.user_email)
        import_ticket(12345, "Individual", self.user_email)
        ticket_type = TicketType.objects.get(name="Individual")
        ticket = Ticket.objects.get(barcode=12345)
        self.assertEqual(ticket.barcode, 12345)
        self.assertEqual(ticket.email, self.user_email)
        self.assertEqual(ticket.type, ticket_type)
        self.assertEqual(ticket.user, user)

    def test_simple_import_without_user(self):
        import_ticket(12345, "Individual", self.user_email)
        ticket_type = TicketType.objects.get(name="Individual")
        ticket = Ticket.objects.get(barcode=12345)
        self.assertEqual(ticket.barcode, 12345)
        self.assertEqual(ticket.email, self.user_email)
        self.assertEqual(ticket.type, ticket_type)
        self.assertEqual(ticket.user, None)

    def test_long_ticket_type(self):
        long_type = "Foo" * TicketType.MAX_NAME_LENGTH
        truncated_type = long_type[:TicketType.MAX_NAME_LENGTH]
        import_ticket(12345, long_type, self.user_email)
        ticket_type = TicketType.objects.get(name=truncated_type)
        ticket = Ticket.objects.get(barcode=12345)
        self.assertEqual(ticket.barcode, 12345)
        self.assertEqual(ticket.email, self.user_email)
        self.assertEqual(ticket.type, ticket_type)
        self.assertEqual(ticket.user, None)

    def test_ticket_barcode_already_exists(self):
        ticket_type = TicketType.objects.create(name="Test Type")
        initial_ticket = Ticket.objects.create(
            barcode=12345, email=self.user_email, type=ticket_type, user=None)
        import_ticket(12345, "Test Type", self.user_email)
        [ticket] = Ticket.objects.all()
        self.assertEqual(ticket, initial_ticket)


class PostTicketTests(TestCase):
    """Test posting data to the web hook"""

    def test_posts(self):
        UserModel = get_user_model()
        email = "post@example.com"
        user = UserModel.objects.create_user('Joe', email=email)
        client = Client()
        post_data = {
            "reference": "REF00123456",
            "event_id": 123,
            "event_name": "My Big Event",
            "amount": 0.00,
            "email": "post@example.com",
            "action": "checkout_started",
            "tickets": [
                {"id": 122,
                 "attendee_name": "Test",
                 "attendee_email": "post@example.com",
                 "barcode": 54321,
                 "ticket_type": "Test Ticket",
                 "price": 0.00,
                 }
                ],
            }
        with self.settings(WAFER_TICKETS_SECRET='testsecret'):
            # Check that the secret matters
            response = client.post('/tickets/quicket_hook/?secret=wrongsecret',
                                   json.dumps(post_data),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 403)
            # Check that the ticket gets processed correctly with an
            # existing user
            response = client.post('/tickets/quicket_hook/?secret=testsecret',
                                   json.dumps(post_data),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=54321)
            self.assertEqual(ticket.barcode, 54321)
            self.assertEqual(ticket.email, email)
            self.assertEqual(ticket.user, user)
            # Check duplicate post doesn't change anything
            response = client.post('/tickets/quicket_hook/?secret=testsecret',
                                   json.dumps(post_data),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=54321)
            self.assertEqual(ticket.barcode, 54321)
            self.assertEqual(ticket.email, email)
            self.assertEqual(ticket.user, user)
            # Change email to one that doesn't exist
            post_data['tickets'][0]['attendee_email'] = 'none@example.com'
            post_data['tickets'][0]['barcode'] = 65432
            response = client.post('/tickets/quicket_hook/?secret=testsecret',
                                   json.dumps(post_data),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=65432)
            self.assertEqual(ticket.barcode, 65432)
            self.assertEqual(ticket.email, 'none@example.com')
            self.assertEqual(ticket.user, None)
