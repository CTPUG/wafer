import json

from django.test import TestCase, Client

from wafer.tests.api_utils import SortedResultsClient
from wafer.tests.utils import create_user
from wafer.tickets.views import import_ticket
from wafer.tickets.models import Ticket, TicketType


class ImportTicketTests(TestCase):
    def setUp(self):
        self.user_email = "user@example.com"

    def test_simple_import_with_user(self):
        user = create_user("User Foo", email=self.user_email)
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
        email = "post@example.com"
        user = create_user('Joe', email=email)
        client = Client()
        post_data = {
                "ticket_type": "Test Type",
                "barcode": "54321",
                "email": "post@example.com"
            }
        with self.settings(WAFER_TICKETS_SECRET='testsecret'):
            # Check that the secret matters
            response = client.post('/tickets/zapier_guest_hook/',
                                   json.dumps(post_data),
                                   content_type="application/json",
                                   HTTP_X_ZAPIER_SECRET='wrongsecret')
            self.assertEqual(response.status_code, 403)
            # Check that the ticket gets processed correctly with an
            # existing user
            response = client.post('/tickets/zapier_guest_hook/',
                                   json.dumps(post_data),
                                   content_type="application/json",
                                   HTTP_X_ZAPIER_SECRET='testsecret')
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=54321)
            self.assertEqual(ticket.barcode, 54321)
            self.assertEqual(ticket.email, email)
            self.assertEqual(ticket.user, user)
            # Check duplicate post doesn't change anything
            response = client.post('/tickets/zapier_guest_hook/',
                                   json.dumps(post_data),
                                   content_type="application/json",
                                   HTTP_X_ZAPIER_SECRET='testsecret')
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=54321)
            self.assertEqual(ticket.barcode, 54321)
            self.assertEqual(ticket.email, email)
            self.assertEqual(ticket.user, user)
            # Change email to one that doesn't exist
            post_data['email'] = 'none@example.com'
            post_data['barcode'] = 65432
            response = client.post('/tickets/zapier_guest_hook/',
                                   json.dumps(post_data),
                                   content_type="application/json",
                                   HTTP_X_ZAPIER_SECRET='testsecret')
            self.assertEqual(response.status_code, 200)
            ticket = Ticket.objects.get(barcode=65432)
            self.assertEqual(ticket.barcode, 65432)
            self.assertEqual(ticket.email, 'none@example.com')
            self.assertEqual(ticket.user, None)
            # Test cancelation
            response = client.post('/tickets/zapier_cancel_hook/',
                                   json.dumps(post_data),
                                   content_type="application/json",
                                   HTTP_X_ZAPIER_SECRET='testsecret')
            self.assertEqual(response.status_code, 200)
            # Check ticket has been deleted
            self.assertFalse(Ticket.objects.filter(barcode=65432).exists())
            # Check earlier ticket still exists
            self.assertEqual(Ticket.objects.filter(barcode=54321).count(), 1)


class TicketTypesViewSetTests(TestCase):
    def setUp(self):
        create_user("super", superuser=True)
        self.client = SortedResultsClient(sort_key="name")
        self.client.login(username="super", password="super_password")

    def mk_result(self, ticket_type):
        return {
            "id": ticket_type.id,
            "name": ticket_type.name,
        }

    def test_list_ticket_types(self):
        ticket_type_1 = TicketType.objects.create(name="Test Type 1")
        ticket_type_2 = TicketType.objects.create(name="Test Type 2")
        response = self.client.get("/tickets/api/tickettypes/")
        self.assertEqual(
            response.data["results"], [
                self.mk_result(ticket_type_1),
                self.mk_result(ticket_type_2),
            ]
        )

    def test_retrieve_ticket_type(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        response = self.client.get(
            "/tickets/api/tickettypes/%d/" % (ticket_type.id,)
        )
        self.assertEqual(response.data, self.mk_result(ticket_type))

    def test_create_ticket_type(self):
        response = self.client.post(
            "/tickets/api/tickettypes/",
            data={"name": "New Ticket Type"},
            format="json",
        )
        [ticket_type] = TicketType.objects.all()
        self.assertEqual(response.data, self.mk_result(ticket_type))
        self.assertEqual(ticket_type.name, "New Ticket Type")

    def test_update_ticket_type(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket_type_id = ticket_type.id
        response = self.client.put(
            "/tickets/api/tickettypes/%d/" % (ticket_type.id,),
            data={"name": "New Type Name"},
            format="json",
        )
        [ticket_type] = TicketType.objects.all()
        self.assertEqual(ticket_type.id, ticket_type_id)
        self.assertEqual(response.data, self.mk_result(ticket_type))
        self.assertEqual(ticket_type.name, "New Type Name")

    def test_patch_ticket_type(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket_type_id = ticket_type.id
        response = self.client.patch(
            "/tickets/api/tickettypes/%d/" % (ticket_type.id,),
            data={"name": "New Type Name"},
            format="json",
        )
        [ticket_type] = TicketType.objects.all()
        self.assertEqual(ticket_type.id, ticket_type_id)
        self.assertEqual(response.data, self.mk_result(ticket_type))
        self.assertEqual(ticket_type.name, "New Type Name")

    def test_delete_ticket_type(self):
        ticket_type_1 = TicketType.objects.create(name="Test Type 1")
        ticket_type_2 = TicketType.objects.create(name="Test Type 1")
        response = self.client.delete(
            "/tickets/api/tickettypes/%d/" % (ticket_type_1.id,),
        )
        [ticket_type] = TicketType.objects.all()
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ticket_type, ticket_type_2)


class TicketsViewSetTests(TestCase):
    def setUp(self):
        create_user("super", superuser=True)
        self.client = SortedResultsClient(sort_key="barcode")
        self.client.login(username="super", password="super_password")

    def mk_result(self, ticket):
        return {
            "barcode": ticket.barcode,
            "email": ticket.email,
            "type": ticket.type.id,
            "user": None,
        }

    def test_list_tickets(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket_1 = Ticket.objects.create(
            barcode=1, email="a@example.com", type=ticket_type)
        ticket_2 = Ticket.objects.create(
            barcode=2, email="b@example.com", type=ticket_type)
        response = self.client.get("/tickets/api/tickets/")
        self.assertEqual(
            response.data["results"], [
                self.mk_result(ticket_1),
                self.mk_result(ticket_2),
            ]
        )

    def test_retrieve_ticket(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket = Ticket.objects.create(
            barcode=1, email="a@example.com", type=ticket_type)
        response = self.client.get(
            "/tickets/api/tickets/%d/" % (ticket.barcode,)
        )
        self.assertEqual(response.data, self.mk_result(ticket))

    def test_create_ticket(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        response = self.client.post(
            "/tickets/api/tickets/",
            data={
                "barcode": 123,
                "email": "joe@example.com",
                "type": ticket_type.id,
                "user": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        [ticket] = Ticket.objects.all()
        self.assertEqual(response.data, self.mk_result(ticket))
        self.assertEqual(ticket.barcode, 123)
        self.assertEqual(ticket.email, "joe@example.com")
        self.assertEqual(ticket.type, ticket_type)
        self.assertEqual(ticket.user, None)

    def test_create_ticket_without_barcode(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        response = self.client.post(
            "/tickets/api/tickets/",
            data={
                "email": "joe@example.com",
                "type": ticket_type.id,
                "user": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), [
            "barcode required during ticket creation"])
        self.assertEqual(Ticket.objects.count(), 0)

    def test_update_ticket(self):
        ticket_type_1 = TicketType.objects.create(name="Test Type 1")
        ticket_type_2 = TicketType.objects.create(name="Test Type 1")
        ticket = Ticket.objects.create(
            barcode=123, email="a@example.com", type=ticket_type_1)
        response = self.client.put(
            "/tickets/api/tickets/%d/" % (ticket.barcode,),
            data={
                "email": "b@example.com",
                "type": ticket_type_2.id,
                "user": None,
            },
            format="json",
        )
        [ticket] = Ticket.objects.all()
        self.assertEqual(ticket.barcode, 123)
        self.assertEqual(response.data, self.mk_result(ticket))
        self.assertEqual(ticket.email, "b@example.com")
        self.assertEqual(ticket.type, ticket_type_2)
        self.assertEqual(ticket.user, None)

    def test_update_ticket_with_barcode(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket = Ticket.objects.create(
            barcode=123, email="a@example.com", type=ticket_type)
        response = self.client.put(
            "/tickets/api/tickets/%d/" % (ticket.barcode,),
            data={
                "barcode": 456,
                "email": "b@example.com",
                "type": ticket_type.id,
                "user": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), [
            "barcode forbidden during ticket update"])
        [ticket_new] = Ticket.objects.all()
        self.assertEqual(ticket_new, ticket)

    def test_patch_ticket(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket = Ticket.objects.create(
            barcode=123, email="a@example.com", type=ticket_type)
        response = self.client.patch(
            "/tickets/api/tickets/%d/" % (ticket.barcode,),
            data={
                "email": "b@example.com",
            },
            format="json",
        )
        [ticket] = Ticket.objects.all()
        self.assertEqual(ticket.barcode, 123)
        self.assertEqual(response.data, self.mk_result(ticket))
        self.assertEqual(ticket.email, "b@example.com")
        self.assertEqual(ticket.type, ticket_type)
        self.assertEqual(ticket.user, None)

    def test_delete_ticket(self):
        ticket_type = TicketType.objects.create(name="Test Type 1")
        ticket_1 = Ticket.objects.create(
            barcode=123, email="a@example.com", type=ticket_type)
        ticket_2 = Ticket.objects.create(
            barcode=456, email="b@example.com", type=ticket_type)
        response = self.client.delete(
            "/tickets/api/tickets/%d/" % (ticket_1.barcode,),
        )
        [ticket] = Ticket.objects.all()
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ticket, ticket_2)
