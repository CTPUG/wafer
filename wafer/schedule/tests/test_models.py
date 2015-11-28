import datetime as D

from django.test import TestCase

from wafer.schedule.models import Day


class DayTests(TestCase):
    def test_days(self):
        """Create some days and check the results."""
        Day.objects.create(date=D.date(2013, 9, 22))
        Day.objects.create(date=D.date(2013, 9, 23))

        assert Day.objects.count() == 2

        output = ["%s" % x for x in Day.objects.all()]

        assert output == ["Sep 22 (Sun)", "Sep 23 (Mon)"]
