import datetime as D

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.common.exceptions import NoSuchElementException
except ImportError:
    # These need to be non-fatal so the tests can be always loaded
    # and the check in the Runner base class will fail these
    # if stuff isn't loaded
    pass

from unittest import expectedFailure

from django.utils import version
from django.urls import reverse

from wafer.tests.utils import create_user, ChromeTestRunner, FirefoxTestRunner, SELENIUM_WAIT_TIME
from wafer.talks.tests.fixtures import create_talk
from wafer.talks.models import ACCEPTED

from wafer.schedule.models import ScheduleBlock, Venue, Slot, ScheduleItem
from wafer.schedule.tests.test_views import make_pages


class EditorTestsMixin:
    """Define the schedule editor tests independant of the
       selenium webdriver.

       This is combined with the appropriate helper class
       to create the actual test cases."""

    def setUp(self):
        """Create two day table with 3 slots each and 2 venues
           and create some page and talks to populate the schedul"""
        super().setUp()

        self.is_django_5 = version.get_complete_version()[0] >= 5

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

        block1.save()
        block2.save()

        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(block1)
        venue1.blocks.add(block2)

        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(block1)
        venue2.blocks.add(block2)

        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue3.blocks.add(block2)

        self.venues = [venue1, venue2, venue3]

        for x in self.venues:
            x.save()

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

        self.pages = make_pages(6)

        self.block1_slots = [b1_slot1, b1_slot2, b1_slot3]
        self.block2_slots = [b2_slot1, b2_slot2, b2_slot3]

        for x in  self.block1_slots + self.block2_slots:
            x.save()

        self.author_john = create_user('john')
        self.talk1 = create_talk('Test talk 1', status=ACCEPTED, user=self.author_john)
        self.talk2 = create_talk('Test talk 2', status=ACCEPTED, username='james')
        self.talk3 = create_talk('Test talk 3', status=ACCEPTED, username='jess')
        self.talk4 = create_talk('Test talk 4', status=ACCEPTED, user=self.author_john)

        schedue_edit_url = reverse('admin:schedule_editor')
        self.edit_page = f"{self.live_server_url}{schedue_edit_url}"

    def _start(self):
        """Helper method to login as admin and load the editor"""
        self.admin_login()
        self.driver.get(self.edit_page)
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
        )

    def test_access_schedule_editor_no_login(self):
        """Test that the schedule editor isn't accessible if not logged in"""
        self.driver.get(self.edit_page)
        if self.is_django_5:
            header = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
                expected_conditions.presence_of_element_located((By.ID, "header"))
            )
        else:
            header = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        self.assertIn('Django administration', header.text)
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
        if self.is_django_5:
            WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
               expected_conditions.presence_of_element_located((By.ID, "header"))
            )
        else:
            WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
               expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        error = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.CLASS_NAME, "errornote"))
        )
        self.assertIn("authenticated as normal", error.text)
        self.assertIn("not authorized to access this page", error.text)
        # Check that no admin info has loaded
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, 'allTalks')

    def test_access_schedule_editor_admin(self):
        """Test that the schedule editor is accessible for superuser accounts"""
        self._start()
        all_talks_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "All Talks"))
        )
        all_talks_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
        # Ordering should ensure that this is always talk 1
        talk_1_block = tab_pane.find_element(By.CLASS_NAME, "draggable")
        self.assertIn(self.talk1.title, talk_1_block.text)

    def test_drag_talk(self):
        """Test dragging talk behavior"""
        self.assertEqual(ScheduleItem.objects.count(), 0)
        self._start()
        # partial link text to avoid whitespace fiddling
        talks_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Unassigned Talks"))
        )
        talks_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Find the first talk
        source = None
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk1.title in x.text:
                source = x
                break
        # Find the first schedule item in the schedule tabls
        target = self.driver.find_element(By.CSS_SELECTOR, 'td.droppable[data-type=""]')
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        # Pause briefly to make sure the server has a chance to do stuff
        actions.pause(0.5)
        actions.perform()
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.CLASS_NAME, "close"))
        )
        self.assertEqual(ScheduleItem.objects.count(), 1)
        item = ScheduleItem.objects.first()
        self.assertEqual(item.talk, self.talk1)
        # Check that dragged talk is not on the list of unassigned talks
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            self.assertNotIn(self.talk1.title, x.text)
        # Try drag the last talk
        source = None
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk4.title in x.text:
                source = x
                break
        # Find the first schedule item in the schedule tabls
        target = self.driver.find_element(By.CSS_SELECTOR, 'td.droppable[data-type=""]')
        actions.reset_actions()
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.CLASS_NAME, "close"))
        )
        self.assertEqual(ScheduleItem.objects.count(), 2)
        item = ScheduleItem.objects.last()
        self.assertEqual(item.talk, self.talk4)
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            self.assertNotIn(self.talk1.title, x.text)
            self.assertNotIn(self.talk4.title, x.text)

    def test_drag_page(self):
        """Test dragging page behavior"""
        self.assertEqual(ScheduleItem.objects.count(), 0)
        self._start()
        # Drag a page from the siderbar to a slot in the schedule

        page_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Pages"))
        )
        page_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Find the first page
        source = None
        tab_items = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            # We choose page 5 so we're dragging from the middle of the list
            if 'test page 3' in x.text:
                source = x
            tab_items.append(x.text)
        # Find the first schedule item in the schedule tabls
        target = self.driver.find_element(By.CSS_SELECTOR, 'td.droppable[data-type=""]')
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.CLASS_NAME, "close"))
        )
        self.assertEqual(ScheduleItem.objects.count(), 1)
        item = ScheduleItem.objects.first()
        self.assertEqual(item.page, self.pages[3])
        # Check that this hasn't changed the page tab list
        post_drag_tab_items = []
        found = False
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if 'test page 3' in x.text:
                found = True
            post_drag_tab_items.append(x.text)
        self.assertTrue(found)
        self.assertEqual(tab_items, post_drag_tab_items)
        # Try drag the last page
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if 'test page 5' in x.text:
                source = x
                break
        # Find the first schedule item in the schedule tabls
        target = self.driver.find_element(By.CSS_SELECTOR, 'td.droppable[data-type=""]')
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
           expected_conditions.presence_of_element_located((By.CLASS_NAME, "close"))
        )
        self.assertEqual(ScheduleItem.objects.count(), 2)
        item = ScheduleItem.objects.last()
        self.assertEqual(item.page, self.pages[5])
        # Check that this hasn't changed the page tab list
        post_drag_tab_items = []
        found1 = False
        found2 = False
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if 'test page 3' in x.text:
                found1 = True
            if 'test page 5' in x.text:
                found2 = True
            post_drag_tab_items.append(x.text)
        self.assertTrue(found1)
        self.assertTrue(found2)
        self.assertEqual(tab_items, post_drag_tab_items)

    def test_swicth_day(self):
        """Test selecting different days"""
        # Create a couple of schedule items on each day
        item1 = ScheduleItem.objects.create(venue=self.venues[0],
                                           talk_id=self.talk1.pk)

        item2 = ScheduleItem.objects.create(venue=self.venues[1],
                                            talk_id=self.talk2.pk)
        item1.slots.add(self.block1_slots[0])
        item2.slots.add(self.block1_slots[1])

        item3 = ScheduleItem.objects.create(venue=self.venues[0],
                                            page_id=self.pages[0].pk)
        item4 = ScheduleItem.objects.create(venue=self.venues[1],
                                            page_id=self.pages[1].pk)
        item5 = ScheduleItem.objects.create(venue=self.venues[2],
                                            page_id=self.pages[2].pk)
        item3.slots.add(self.block2_slots[0])
        item4.slots.add(self.block2_slots[1])
        item5.slots.add(self.block2_slots[1])

        # Load schedule page
        self._start()
        # Verify we see the expected schedule items on day 1
        td1 = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]'))
        )
        self.assertEqual(td1.tag_name, 'td')
        td2 = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item2.pk}"]')
        self.assertEqual(td2.tag_name, 'td')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item3.pk}"]')
        # Switch day using the schedule block dropdown.
        dropdown_selector = (
            ".col-md-8 .dropdown > button.dropdown-toggle"
        )
        dropdown = WebDriverWait(
            self.driver, SELENIUM_WAIT_TIME
        ).until(
            expected_conditions.element_to_be_clickable((
                By.CSS_SELECTOR, dropdown_selector,
            ))
        )
        self.assertIn("Sep", dropdown.text)
        dropdown.click()

        day_selector = (
            ".col-md-8 .dropdown .dropdown-menu a.dropdown-item"
        )
        days = WebDriverWait(
            self.driver, SELENIUM_WAIT_TIME
        ).until(
            expected_conditions.visibility_of_all_elements_located((
                By.CSS_SELECTOR, day_selector,
            ))
        )
        self.assertGreaterEqual(len(days), 2)
        self.assertIn("Sep", days[1].text)
        days[1].click()

        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.staleness_of(td1)
        )
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.visibility_of_element_located((
                By.CSS_SELECTOR,
                f'td[data-scheduleitem-id="{item3.pk}"]',
            ))
        )
        # Verify we see the expected schedule items on day 2
        td3 = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item3.pk}"]')
        self.assertEqual(td3.tag_name, 'td')
        td4 = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item4.pk}"]')
        self.assertEqual(td4.tag_name, 'td')
        td5 = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item5.pk}"]')
        self.assertEqual(td5.tag_name, 'td')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item2.pk}"]')

    def test_drag_over_talk(self):
        """Test that dragging over an item replaces it"""
        # Create a schedule with a single item
        item1 = ScheduleItem.objects.create(venue=self.venues[0],
                                           talk_id=self.talk1.pk)
        item1.slots.add(self.block1_slots[0])
        item1.save()
        self._start()
        # Test dragging a talk over an existing talk
        target = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]'))
        )
        talks_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Unassigned Talks")
        talks_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Find the first talk
        source = None
        found = False
        # Find the second talk and verify that talk 1 is not in
        # the Unassigned Talk list
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk2.title in x.text:
                source = x
            if self.talk1.title in x.text:
                found = True
        self.assertFalse(found)
        # Do the drag
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        # Check that schedule item and table entry are correct
        item = ScheduleItem.objects.first()
        self.assertEqual(item.talk, self.talk2)
        target = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]')
        self.assertIn(self.talk2.title, target.text)
        # Check that Unassigned list has been updated correctly
        # (Talk 1 added, and talk 2 removed)
        found2 = False
        found1 = False
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk1.title in x.text:
                found1 = True
            if self.talk2.title in x.text:
                found2 = True
        self.assertFalse(found2)
        self.assertTrue(found1)

    def test_drag_over_page(self):
        """Test that dragging over a page with another page works"""
        # Create a schedule with a single item
        self._start()

        item1 = ScheduleItem.objects.create(venue=self.venues[0],
                                            page_id=self.pages[0].pk)
        item1.slots.add(self.block1_slots[0])
        item1.save()
        self._start()
        # Test dragging a page over an existing page
        target = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]'))
        )
        page_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Pages")
        page_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Find the source page
        source = None
        # Find the second talk and verify that talk 1 is not in
        # the Unassigned Talk list
        before = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if 'test page 3' in x.text:
                source = x
            before.append(x.text)
        # Do the drag
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        # Check that schedule item and table entry are correct
        item = ScheduleItem.objects.first()
        self.assertEqual(item.page, self.pages[3])
        target = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item1.pk}"]')
        self.assertIn('test page 3', target.text)
        # Check that the list is unchanged
        after = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if 'test page 3' in x.text:
                source = x
            after.append(x.text)
        self.assertEqual(before, after)

    def test_adding_clash(self):
        """Test that introducing a speaker clash causes the
           error section to be updated"""
        item1 = ScheduleItem.objects.create(venue=self.venues[0],
                                           talk_id=self.talk1.pk)
        item1.slots.add(self.block1_slots[0])
        item1.save()
        item2 = ScheduleItem.objects.create(venue=self.venues[1],
                                           talk_id=self.talk2.pk)
        item2.slots.add(self.block1_slots[0])
        item2.save()
        self._start()
        # Verify that there are no validation errors
        validation = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertFalse(validation.is_displayed())
        # Drag a talk into a clashing slot
        target = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item2.pk}"]')
        talks_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Unassigned Talks")
        talks_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Find the first talk
        source = None
        found = False
        # Find the second talk and verify that talk 1 is not in
        # the Unassigned Talk list
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk4.title in x.text:
                source = x
            if self.talk1.title in x.text:
                found = True
        self.assertFalse(found)
        # Do the drag
        actions = webdriver.ActionChains(self.driver)
        actions.drag_and_drop(source, target)
        actions.pause(0.5)
        actions.perform()
        # Verify error block is displayed
        self.assertTrue(validation.is_displayed())
        error_item = validation.find_element(By.TAG_NAME, "li")
        self.assertIn('Common speaker', error_item.text)

    def test_removing_clash(self):
        """Test that removing a speaker clash causes the
           error section to be cleared"""
        item1 = ScheduleItem.objects.create(venue=self.venues[0],
                                           talk_id=self.talk1.pk)
        item1.slots.add(self.block1_slots[0])
        item1.save()
        item2 = ScheduleItem.objects.create(venue=self.venues[1],
                                           talk_id=self.talk4.pk)
        item2.slots.add(self.block1_slots[0])
        item2.save()
        self._start()
        # Verify that there are validation errors
        validation = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertTrue(validation.is_displayed())
        error_item = validation.find_element(By.TAG_NAME, "li")
        self.assertIn('Common speaker', error_item.text)
        # Delete the clashing talk
        target = self.driver.find_element(By.CSS_SELECTOR, f'td[data-scheduleitem-id="{item2.pk}"]')
        close = target.find_element(By.CLASS_NAME, 'close')
        close.click()
        talks_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Unassigned Talks")
        talks_link.click()

        # Wait for the asynchronous validation update after deletion.
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.invisibility_of_element(validation)
        )
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        # Verify we've deleted the clashing talk
        found = None
        # Find the deleted talk in the Unassigned Talk list
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            if self.talk4.title in x.text:
                found = True
        self.assertTrue(found)
        # Verify errors are hidden
        self.assertFalse(validation.is_displayed())
        # Check that the list has been removed
        with self.assertRaises(NoSuchElementException):
            validation.find_element(By.TAG_NAME,"li")

    def test_schedule_duplicate_hides(self):
        """Test that setting num_schedulable to 0 for an item hides it"""
        self.assertEqual(ScheduleItem.objects.count(), 0)
        self._start()
        # Count the number of pages in the list

        page_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Pages"))
        )
        page_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        source = None
        tab_items = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            tab_items.append(x.text)
        self.assertEqual(len(tab_items), 6)
        # Cnange to pages to not be in the schedule
        self.pages[1].num_schedulable = 0
        self.pages[1].save()

        self.pages[4].num_schedulable = 0
        self.pages[4].save()
        # Reload the page
        self.driver.refresh()
        # Count the number of pages in the list

        page_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Pages"))
        )
        page_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        source = None
        tab_items = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            tab_items.append(x.text)
        self.assertEqual(len(tab_items), 4)

        # Check that numbers > 1 are included in the list
        self.pages[1].num_schedulable = 4
        self.pages[1].save()

        self.pages[2].num_schedulable = 3
        self.pages[2].save()
        # Reload the page
        self.driver.refresh()

        page_link = WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Pages"))
        )
        page_link.click()
        tab_pane = None
        for pane in self.driver.find_elements(By.CLASS_NAME, "tab-pane"):
            if 'active' in pane.get_attribute('class'):
                tab_pane = pane
                break
        source = None
        tab_items = []
        for x in tab_pane.find_elements(By.CLASS_NAME, 'draggable'):
            tab_items.append(x.text)
        self.assertEqual(len(tab_items), 5)

class ChromeScheduleEditorTests(EditorTestsMixin, ChromeTestRunner):

    def _test_extend_item(self, item_type, target_index):
        """Extend one item while preserving its original slot."""
        content = (
            {"talk": self.talk1}
            if item_type == "talk"
            else {"page": self.pages[0]}
        )
        item = ScheduleItem.objects.create(
            venue=self.venues[0], **content
        )
        original_slot = self.block1_slots[0]
        target_slot = self.block1_slots[target_index]
        item.slots.add(original_slot)
        self._start()

        source = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-scheduleitem-id="{item.pk}"]'
            f'[data-slot="{original_slot.pk}"]',
        )
        target = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-venue="{self.venues[0].pk}"]'
            f'[data-slot="{target_slot.pk}"]',
        )

        webdriver.ActionChains(self.driver).drag_and_drop(
            source, target
        ).perform()

        expected_slots = {original_slot.pk, target_slot.pk}
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: set(
                item.slots.values_list("pk", flat=True)
            ) == expected_slots
        )
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.staleness_of(source)
        )

        self.assertEqual(ScheduleItem.objects.count(), 1)

        # Confirm both placements also survive a fresh page load.
        self.driver.refresh()
        for slot in (original_slot, target_slot):
            cell = WebDriverWait(
                self.driver, SELENIUM_WAIT_TIME
            ).until(
                expected_conditions.presence_of_element_located((
                    By.CSS_SELECTOR,
                    f'td[data-scheduleitem-id="{item.pk}"]'
                    f'[data-slot="{slot.pk}"]',
                ))
            )
            title = (
                self.talk1.title
                if item_type == "talk"
                else self.pages[0].name
            )
            self.assertIn(title, cell.text)

    def test_extend_talk_adjacent(self):
        self._test_extend_item("talk", 1)

    def test_extend_talk_non_contiguous(self):
        self._test_extend_item("talk", 2)

    def test_extend_page_adjacent(self):
        self._test_extend_item("page", 1)

    def test_extend_page_non_contiguous(self):
        self._test_extend_item("page", 2)

    def _test_remove_item_slots(self, item_type):
        """Remove one slot, then delete the final placement."""
        content = (
            {"talk": self.talk1}
            if item_type == "talk"
            else {"page": self.pages[0]}
        )
        item = ScheduleItem.objects.create(
            venue=self.venues[0], **content
        )
        first_slot, last_slot = self.block1_slots[:2]
        item.slots.add(first_slot, last_slot)
        self._start()

        first_cell = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-scheduleitem-id="{item.pk}"]'
            f'[data-slot="{first_slot.pk}"]',
        )
        first_cell.find_element(By.CLASS_NAME, "close").click()

        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: set(
                item.slots.values_list("pk", flat=True)
            ) == {last_slot.pk}
        )
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: not first_cell.get_attribute(
                "data-scheduleitem-id"
            )
        )
        self.assertEqual(ScheduleItem.objects.count(), 1)

        self.driver.refresh()
        last_cell = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-scheduleitem-id="{item.pk}"]'
            f'[data-slot="{last_slot.pk}"]',
        )
        last_cell.find_element(By.CLASS_NAME, "close").click()

        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: not ScheduleItem.objects.filter(
                pk=item.pk
            ).exists()
        )
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: not last_cell.get_attribute(
                "data-scheduleitem-id"
            )
        )
        self.assertEqual(ScheduleItem.objects.count(), 0)

        if item_type == "talk":
            self.driver.find_element(
                By.PARTIAL_LINK_TEXT, "Unassigned Talks"
            ).click()
            unassigned = self.driver.find_element(
                By.ID, f"talk{self.talk1.pk}"
            )
            self.assertTrue(unassigned.is_displayed())

    def test_remove_talk_slots(self):
        self._test_remove_item_slots("talk")

    def test_remove_page_slots(self):
        self._test_remove_item_slots("page")

    def _test_rejected_extension(self, occupied):
        item = ScheduleItem.objects.create(
            venue=self.venues[0], talk=self.talk1
        )
        original_slot = self.block1_slots[0]
        target_slot = self.block1_slots[1]
        item.slots.add(original_slot)

        target_venue = self.venues[0] if occupied else self.venues[1]
        other = None
        if occupied:
            other = ScheduleItem.objects.create(
                venue=target_venue, talk=self.talk2
            )
            other.slots.add(target_slot)

        self._start()
        source = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-scheduleitem-id="{item.pk}"]',
        )
        target = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-venue="{target_venue.pk}"]'
            f'[data-slot="{target_slot.pk}"]',
        )

        webdriver.ActionChains(self.driver).drag_and_drop(
            source, target
        ).perform()

        alert = WebDriverWait(
            self.driver, SELENIUM_WAIT_TIME
        ).until(expected_conditions.alert_is_present())
        expected_message = (
            "Please choose an empty slot to extend this item."
            if occupied
            else "Additional slots must be in the same venue."
        )
        self.assertEqual(alert.text, expected_message)
        alert.accept()

        item.refresh_from_db()
        self.assertEqual(item.venue_id, self.venues[0].pk)
        self.assertSetEqual(
            set(item.slots.values_list("pk", flat=True)),
            {original_slot.pk},
        )
        self.assertEqual(
            ScheduleItem.objects.count(), 2 if occupied else 1
        )
        if other:
            other.refresh_from_db()
            self.assertEqual(other.talk_id, self.talk2.pk)
            self.assertSetEqual(
                set(other.slots.values_list("pk", flat=True)),
                {target_slot.pk},
            )

    def test_extend_into_occupied_cell_rejected(self):
        self._test_rejected_extension(occupied=True)

    def test_extend_into_other_venue_rejected(self):
        self._test_rejected_extension(occupied=False)

    def test_extend_new_talk_without_refresh(self):
        """A newly placed talk can immediately gain another slot."""
        self._start()
        self.driver.find_element(
            By.PARTIAL_LINK_TEXT, "Unassigned Talks"
        ).click()
        source = self.driver.find_element(
            By.ID, f"talk{self.talk1.pk}"
        )
        first_slot, next_slot = self.block1_slots[:2]
        first_cell = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-venue="{self.venues[0].pk}"]'
            f'[data-slot="{first_slot.pk}"]',
        )

        webdriver.ActionChains(self.driver).drag_and_drop(
            source, first_cell
        ).perform()


        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: first_cell.get_attribute("draggable") == "true"
            and first_cell.get_attribute("data-scheduleitem-id")
            not in (None, "", "null")
        )
        item = ScheduleItem.objects.get(talk=self.talk1)


        # Extend directly from the new cell without refreshing.
        target = self.driver.find_element(
            By.CSS_SELECTOR,
            f'td[data-venue="{self.venues[0].pk}"]'
            f'[data-slot="{next_slot.pk}"]',
        )
        webdriver.ActionChains(self.driver).drag_and_drop(
            first_cell, target
        ).perform()


        expected_slots = {first_slot.pk, next_slot.pk}
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            lambda driver: set(
                item.slots.values_list("pk", flat=True)
            ) == expected_slots
        )
        WebDriverWait(self.driver, SELENIUM_WAIT_TIME).until(
            expected_conditions.staleness_of(first_cell)
        )
        self.assertEqual(ScheduleItem.objects.count(), 1)



class FirefoxSchedultEditorTests(EditorTestsMixin, FirefoxTestRunner):
    # We explictly mark the tests we expect to fail due to
    # https://bugzilla.mozilla.org/show_bug.cgi?id=1515879
    # as expectedFailure, so we can run these in github actions
    # with sensible results (and hopefully see when the bug gets
    # fixed).

    @expectedFailure
    def test_drag_talk(self):
        super().test_drag_talk()

    @expectedFailure
    def test_drag_page(self):
        super().test_drag_page()

    @expectedFailure
    def test_drag_over_talk(self):
        super().test_drag_over_talk()

    @expectedFailure
    def test_drag_over_page(self):
        super().test_drag_over_page()

    @expectedFailure
    def test_adding_clash(self):
        super().test_adding_clash()
