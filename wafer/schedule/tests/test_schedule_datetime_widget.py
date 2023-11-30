import datetime as D

try:
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.common.exceptions import NoSuchElementException
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
        self.block1.save()
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(self.block1)

        self.slot1 =  Slot(start_time=D.datetime(2013, 9, 22, 12, 0, 0,
                                            tzinfo=D.timezone.utc),
                      end_time=D.datetime(2013, 9, 22, 13, 0, 0,
                                          tzinfo=D.timezone.utc))
        self.slot1.save()
        self.slot2 =  Slot(previous_slot=self.slot1,
                      end_time=D.datetime(2013, 9, 22, 14, 0, 0,
                                          tzinfo=D.timezone.utc))

    def check_clock_button(self):
        """Standard check for the clock button contents"""
        # Find the clock button
        clock_button = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'clock-icon'))
        )
        # Check that the list isn't visible before we click
        clock_box = self.driver.find_element(By.ID, 'clockbox0')
        style = clock_box.get_attribute('style')
        self.assertIn('display: none', style)
        clock_button.click()
        timelist =  WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'timelist'))
        )
        clock_box = self.driver.find_element(By.ID, 'clockbox0')
        style = clock_box.get_attribute('style')
        self.assertIn('display: block', style)
        seen_times = []
        for li in timelist.find_elements(By.TAG_NAME, 'li'):
            ahref = li.find_element(By.TAG_NAME, 'a')
            seen_times.append(ahref.text.strip())
        for time in range(8, 21):
            time_str = f'{time:02d}:00'
            self.assertIn(time_str, seen_times)

    def test_datetime_widget_slot_admin_changelist(self):
        """Test that the datetime widget lists the desired times in the list view"""
        self.admin_login()
        # Navigate to the slot list page
        slot_admin_list_url = reverse('admin:schedule_slot_changelist')
        self.driver.get(f"{self.live_server_url}{slot_admin_list_url}")
        self.check_clock_button()

    def test_datetime_widget_slot_admin_change(self):
        """Test that the datetime widget lists the desired times
           on the individual slot admin page"""
        # We need to specify kwargs as an explicit dict
        self.admin_login()
        slot_admin_change_url = reverse('admin:schedule_slot_change',
                                        kwargs={'object_id': self.slot1.pk})
        self.driver.get(f"{self.live_server_url}{slot_admin_change_url}")
        self.check_clock_button()

    def test_datetime_widget_schedule_block_admin(self):
        """Test that the datetime widget lists the desired times"""
        self.admin_login()
        # Navigate to the schedule block page
        block_admin_change_url = reverse('admin:schedule_scheduleblock_change',
                                         kwargs={'object_id': self.block1.id})
        self.driver.get(f"{self.live_server_url}{block_admin_change_url}")
        self.check_clock_button()


class ChromeScheduleEditorTests(ScheduleDateTimeJSMixin, ChromeTestRunner):
    pass


class FirefoxSchedultEditorTests(ScheduleDateTimeJSMixin, FirefoxTestRunner):
    pass
