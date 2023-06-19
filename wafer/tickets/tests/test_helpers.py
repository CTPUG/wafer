from django.test import TestCase

from wafer.tests.utils import create_user
from wafer.tickets.views import import_ticket
from wafer.tickets.models import Ticket, TicketType, user_is_registered, get_user_ticket_types


class TicketsHelperFunctionTests(TestCase):
    """Test the helper functions"""

    def setUp(self):
        self.user_email = "user2@example.com"
        self.user = create_user("User Foo 2", email=self.user_email)

    def test_user_is_registered(self):
        self.assertFalse(user_is_registered(self.user))
        import_ticket(77777, "Individual", self.user_email)
        # Check the we are now registered
        self.assertTrue(user_is_registered(self.user))

    def test_get_user_ticket_types(self):
        import_ticket(77777, "Individual", self.user_email)
        ticket_type = TicketType.objects.get(name="Individual")
        self.assertEqual(get_user_ticket_types(self.user), set([ticket_type]))
        # Buy a second ticket with a different type
        import_ticket(888888, "Corp", self.user_email)
        type2 =  TicketType.objects.get(name="Corp")
        self.assertEqual(get_user_ticket_types(self.user), set([ticket_type, type2]))

