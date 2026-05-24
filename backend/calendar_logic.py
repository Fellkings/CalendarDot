from datetime import datetime
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from backend.models import Event, RecurrenceRule

FREQ_MAP = {
    "DAILY": DAILY,
    "WEEKLY": WEEKLY,
    "MONTHLY": MONTHLY,
    "YEARLY": YEARLY
}

def get_event_occurrences(event: Event, rule: RecurrenceRule, view_start: datetime, view_end: datetime):
    #генерация список дат для события в заданном окне просмотра
    if not rule:
        if view_start <= event.start_time <= view_end:
            return [event.start_time]
        return []

    freq = FREQ_MAP.get(rule.frequency, DAILY)
    
    rr = rrule(
        freq=freq,
        dtstart=event.start_time,
        interval=rule.interval or 1,
        until=rule.until,
        count=rule.count
    )

    return rr.between(view_start, view_end, inc=True)