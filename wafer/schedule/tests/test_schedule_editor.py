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
from wafer.tests.utils import create_user, ChromeTestRunner, FirefoxTestRunner
from wafer.talks.tests.fixtures import create_talk
from wafer.talks.models import ACCEPTED

from wafer.schedule.models import ScheduleBlock, Venue, Slot, ScheduleItem
from wafer.schedule.tests.test_views import make_pages, make_items


class EditorTestsMixin:
    """Define the schedule editor tests independant of the
       selenium webdriver.

       This is combined with the appropriate helper class
       to create the actual test cases."""

    def setUp(self):
        """Create two day table with 3 slots each and 2 venues
           and create some page and talks to populate the schedul"""
        super().setUp()
        # Schedule is
        # Day1
        #         Venue 1     Venue 2
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # 12-13   Item3       Item6
        # Day 2
        #         Venue 1     Venue 2   Venue 3
        # 10-11   Item7       Item10    Item13
        # 11-12   Item8       Item11    Item14
        # 12-13   Item9       Item12    Item15
        block1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=D.timezone.utc),
            )

        block2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=D.timezone.utc),
            )

        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(block1)
        venue1.blocks.add(block2)

        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(block1)
        venue2.blocks.add(block2)

        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue3.blocks.add(block2)

        self.venues = [venue1, venue2, venue3]

        b1_start1 = D.datetime(2013, 9, 22, 10, 0, 0,
                               tzinfo=D.timezone.utc)
        b1_start2 = D.datetime(2013, 9, 22, 11, 0, 0,
                               tzinfo=D.timezone.utc)
        b1_start3 = D.datetime(2013, 9, 22, 12, 0, 0,
                               tzinfo=D.timezone.utc)
        b1_end = D.datetime(2013, 9, 22, 13, 0, 0,
                            tzinfo=D.timezone.utc)

        b1_slot1 = Slot(start_time=b1_start1,
                        end_time=b1_start2)
        b1_slot2 = Slot(previous_slot=b1_slot1,
                        end_time=b1_start3)
        b1_slot3 = Slot(previous_slot=b1_slot2,
                        end_time=b1_end)

        b2_start1 = D.datetime(2013, 9, 23, 10, 0, 0,
                               tzinfo=D.timezone.utc)
        b2_start2 = D.datetime(2013, 9, 23, 11, 0, 0,
                               tzinfo=D.timezone.utc)
        b2_start3 = D.datetime(2013, 9, 23, 12, 0, 0,
                               tzinfo=D.timezone.utc)
        b2_end = D.datetime(2013, 9, 23, 13, 0, 0,
                            tzinfo=D.timezone.utc)

        b2_slot1 = Slot(start_time=b2_start1,
                       end_time=b2_start2)
        b2_slot2 = Slot(previous_slot=b2_slot1,
                        end_time=b2_start3)
        b2_slot3 = Slot(previous_slot=b2_slot2,
                        end_time=b2_end)

        self.pages = make_pages(12)

        self.block1_slots = [b1_slot1, b1_slot2, b1_slot3]
        self.block2_slots = [b2_slot1, b2_slot2, b2_slot3]

        self.talk1 = create_talk('Test talk 1', status=ACCEPTED, username='john')
        self.talk2 = create_talk('Test talk 2', status=ACCEPTED, username='james')
        self.talk3 = create_talk('Test talk 3', status=ACCEPTED, username='jess')
        self.talk4 = create_talk('Test talk 4', status=ACCEPTED, username='jonah')

        schedue_edit_url = reverse('admin:schedule_editor')
        self.edit_page = f"{self.live_server_url}{schedue_edit_url}"

    def test_access_schedule_editor_no_login(self):
        """Test that the schedule editor isn't accessible if not logged in"""
        self.driver.get(self.edit_page)
        header = WebDriverWait(self.driver, 10).until(
           expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertEqual('Django administration', header.text)
        login = self.driver.find_element(By.ID, "login-form")
        self.assertIsNotNone(login)
        self.assertIn('login', login.get_attribute('action'))
        # Check that no admin info has loaded
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, 'allTalks')

    def test_access_schedule_editor_no_super(self):
        """Test that the schedule editor isn't accessible for non-superuser accounts"""
        self.normal_login()
        self.driver.get(self.edit_page)
        WebDriverWait(self.driver, 10).until(
           expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        error = self.driver.find_element(By.CLASS_NAME, "errornote")
        self.assertIn("authenticated as normal", error.text)
        self.assertIn("not authorized to access this page", error.text)
        # Check that no admin info has loaded
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, 'allTalks')

    def test_access_schedule_editor_admin(self):
        """Test that the schedule editor is accessible for superuser accounts"""
        self.admin_login()
        self.driver.get(self.edit_page)
        WebDriverWait(self.driver, 10).until(
           expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        all_talks = self.driver.find_element(By.ID, "allTalks")
        self.assertTrue(all_talks is not None)
        # Ordering should ensure that this is always talk 1
        talk_1_block = all_talks.find_element(By.TAG_NAME, "div")
        self.assertIn(self.talk1.title, talk_1_block.text)

    def test_drag_talk(self):
        """Test dragging talk behavior"""
        self.admin_login()
        self.driver.get(self.edit_page)
        # Drag a talk from the siderbar to a slot in the schedule
        # Check that dragged talk is not on the list of unassigned talks
        # Drag a talk from one slot to another

    def test_drag_page(self):
        """Test dragging page behavior"""
        self.admin_login()
        self.driver.get(self.edit_page)
        # Drag a page from the siderbar to a slot in the schedule
        # Check that this doesn't change the unassigned list
        # Drag a page from one spot to another

    def test_swicth_day(self):
        """Test selecting different days"""
        self.admin_login()
        self.driver.get(self.edit_page)

    def test_remove_talk(self):
        """Test removing talks"""
        self.admin_login()
        self.driver.get(self.edit_page)
        # Test delete button
        # Check that unassigned list is updated correctly
        # Test dragging a talk over an existing talk
        # Check that unassigned list is updated correctly

    def test_remove_page(self):
        """Test removing pages"""
        self.admin_login()
        self.driver.get(self.edit_page)
        # Test delete button
        # Test dragging a page over an existing page

    def test_create_invalid_schedule(self):
        """Test that an invalid schedule displays the errors"""
        self.admin_login()
        self.driver.get(self.edit_page)


class ChromeScheduleEditorTests(EditorTestsMixin, ChromeTestRunner):
    pass


class FirefoxSchedultEditorTests(EditorTestsMixin, FirefoxTestRunner):
    pass
