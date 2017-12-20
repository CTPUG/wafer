from datetime import datetime, timedelta
from django.utils import timezone


def get_start_end_for_scheduleitem(si):
    start = timezone.make_aware(datetime.strptime(
        si.get_start_time(), "%b %d (%a), %H:%M"
    ), timezone.get_default_timezone())

    end = start + timedelta(minutes=si.get_duration_minutes())

    return (start, end)
