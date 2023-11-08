import datetime as D

from django.utils import timezone

from wafer.pages.models import Page
from wafer.tests.utils import ChromeTestRunner, FirefoxTestRunner

from wafer.schedule.models import Venue, Slot, ScheduleBlock
from wafer.schedule.tests.test_views import make_pages, make_items


class ScheduleDateTimeJSMixin:
    """Test the custom datetime widget"""

    def setUp(self):
        """Create venue, block and slots so we use the slot admin page"""
        super().setUp()
        block1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=D.timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(block1)

        slot1 =  Slot(start_time=D.datetime(2013, 9, 22, 12, 0, 0,
                                            tzinfo=D.timezone.utc),
                      end_time=D.datetime(2013, 9, 22, 13, 0, 0,
                                          tzinfo=D.timezone.utc))
        slot2 =  Slot(previous_slot=slot1,
                      end_time=D.datetime(2013, 9, 22, 14, 0, 0,
                                          tzinfo=D.timezone.utc))

    def test_datetime_widget(self):
        """Test that the datetime widget lists the desired times"""
        self.admin_login()
    

class ChromeScheduleEditorTests(ScheduleDateTimeJSMixin, ChromeTestRunner):
    pass


class FirefoxSchedultEditorTests(ScheduleDateTimeJSMixin, FirefoxTestRunner):
    pass
