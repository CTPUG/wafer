from django.contrib.admin.sites import AdminSite

from django.test import TestCase, RequestFactory

from wafer.tickets.models import TicketType, TicketTypeTag, Ticket
from wafer.tickets.admin import TicketTypeAdmin

from  wafer.tests.utils import create_user

class TicketTypeAdminTests(TestCase):

    def setUp(self):
        self.user_emails = ["user%d@example.com" % num for num in range(5)]
        # create some tags
        self.tag_z = TicketTypeTag.objects.create(name='tag z')
        self.tag_a = TicketTypeTag.objects.create(name='tag a')
        self.tag_d = TicketTypeTag.objects.create(name='tag d')
        # Create some type
        self.type_sponsor = TicketType.objects.create(name='Sponsor')
        self.type_student = TicketType.objects.create(name='Student')
        self.admin_model = TicketTypeAdmin(model=TicketType, admin_site=AdminSite())

        self.admin_user = create_user('ticket_admin', superuser=True)
        self.request_factory = RequestFactory()


    def test_tags(self):
        """Test that get_tags works as expected"""
        # Add tags
        self.type_sponsor.tags.add(self.tag_z)
        self.type_sponsor.tags.add(self.tag_a)

        self.type_student.tags.add(self.tag_d)
        self.type_student.tags.add(self.tag_z)
        self.type_student.tags.add(self.tag_a)

        self.assertEqual(self.type_sponsor.get_tags(), 'tag a, tag z')
        self.assertEqual(self.type_student.get_tags(), 'tag a, tag d, tag z')

    def test_ticket_counts(self):
        """Test the get_count query on the admin model"""

        # Buy some tickets
        Ticket.objects.create(email=self.user_emails[0], type=self.type_sponsor,
                              barcode='1234')
        Ticket.objects.create(email=self.user_emails[1], type=self.type_sponsor,
                              barcode='2345')
        Ticket.objects.create(email=self.user_emails[2], type=self.type_sponsor,
                              barcode='3456')

        request = self.request_factory.get("/")
        request.user = self.admin_user
        qs = self.admin_model.get_queryset(request)
        self.assertEqual(self.admin_model.get_ticket_count(qs[0]), 3)
        self.assertEqual(self.admin_model.get_ticket_count(qs[1]), 0)

        Ticket.objects.create(email=self.user_emails[3], type=self.type_student,
                              barcode='4321')
        ticket5 = Ticket.objects.create(email=self.user_emails[4], type=self.type_student,
                                        barcode='1111')

        qs = self.admin_model.get_queryset(request)
        self.assertEqual(self.admin_model.get_ticket_count(qs[0]), 3)
        self.assertEqual(self.admin_model.get_ticket_count(qs[1]), 2)

        ticket5.delete()

        qs = self.admin_model.get_queryset(request)
        self.assertEqual(self.admin_model.get_ticket_count(qs[0]), 3)
        self.assertEqual(self.admin_model.get_ticket_count(qs[1]), 1)
