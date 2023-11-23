import datetime as D

try:
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
except ImportError:
    # These need to be non-fatal so the tests can be always loaded
    # and the check in the Runner base class will fail these
    # if stuff isn't loaded
    pass


from django.utils import timezone
from django.urls import reverse

from wafer.pages.models import Page
from wafer.tests.utils import ChromeTestRunner, FirefoxTestRunner

from wafer.schedule.models import Venue, Slot, ScheduleBlock
from wafer.schedule.tests.test_views import make_pages, make_items


class ScheduleDateTimeJSMixin:
    """Test the custom datetime entries work as expected"""

    def setUp(self):
        """Create venue, block and slots so we use the slot admin page"""
        super().setUp()
        self.block1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=D.timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(self.block1)

        self.slot1 =  Slot(start_time=D.datetime(2013, 9, 22, 12, 0, 0,
                                            tzinfo=D.timezone.utc),
                      end_time=D.datetime(2013, 9, 22, 13, 0, 0,
                                          tzinfo=D.timezone.utc))
        self.slot2 =  Slot(previous_slot=self.slot1,
                      end_time=D.datetime(2013, 9, 22, 14, 0, 0,
                                          tzinfo=D.timezone.utc))

    def test_datetime_widget_slot_admin(self):
        """Test that the datetime widget lists the desired times"""
        self.admin_login()
        # Navigate to the slot list page
        slot_admin_list_url = reverse('admin:schedule_slot_changelist')
        self.driver.get(f"{self.live_server_url}{slot_admin_list_url}")
        # select the time widget
        # Confirm that the expected entries are there
        # Navigate to an indivual slot page
        # We need to specify kwargs as an explicit dict
        slot_admin_change_url = reverse('admin:schedule_slot_change',
                                        kwargs={'object_id': self.slot1.id})
        self.driver.get(f"{self.live_server_url}{slot_admin_change_url}")
        # Also check the widget there

    def test_datetime_widget_schedule_block_admin(self):
        """Test that the datetime widget lists the desired times"""
        self.admin_login()
        # Navigate to the schedule block page
        block_admin_change_url = reverse('admin:schedule_scheduleblock_change',
                                         kwargs={'object_id': self.block1.id})
        self.driver.get(f"{self.live_server_url}{block_admin_change_url}")
        # Check the widget there


class ChromeScheduleEditorTests(ScheduleDateTimeJSMixin, ChromeTestRunner):
    pass


class FirefoxSchedultEditorTests(ScheduleDateTimeJSMixin, FirefoxTestRunner):
    pass
