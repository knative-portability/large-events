import datetime
from collections import namedtuple

EVENT_ATTRIBUTES = [
    'event_id',
    'name',
    'description',
    'author',
    'created_at',
    'event_time']


def equal_times(time_1, time_2):
    """Determines if two times are equal.

    Datetime objects are rounded to the nearest millisecond before comparison.
    Used for comparing Event objects, since MongoDB truncates times to the
    nearest millisecond.

    Strings representing times are directly compared for equality.
    """
    if type(time_1) is type(time_2):
        if isinstance(time_1, datetime.datetime):
            time_1 = time_1.replace(
                microsecond=(time_1.microsecond // 1000) * 1000)
            time_2 = time_2.replace(
                microsecond=(time_2.microsecond // 1000) * 1000)
        return time_1 == time_2
    return False


class Event(namedtuple("EventTuple", EVENT_ATTRIBUTES)):
    """Class for representing events.

    Used to ensure event info is in the correct format when constructing or
    manipulating event info from user input.
    """

    def __new__(cls, **info):
        """Constructs an event object represented by a EventTuple namedtuple.

        Raises a ValueError if any attributes are missing or if extra
        attributes are included.
        """
        if "event_id" not in info:
            info['event_id'] = None
        if '_id' in info:       # found DB-generated ID, override given one
            info['event_id'] = info['_id']
            del info['_id']
        try:
            return super(Event, cls).__new__(cls, **info)
        except TypeError:
            raise ValueError("Event info was formatted incorrectly.")

    def __eq__(self, other):
        """Determines if two events have the same info, excluding event_id."""
        if not isinstance(other, Event):
            return False
        for att in EVENT_ATTRIBUTES:
            if att == 'event_id':
                continue
            if att in ('event_time', 'created_at'):
                if not equal_times(getattr(self, att), getattr(other, att)):
                    return False
            elif getattr(self, att) != getattr(other, att):
                return False
        return True

    def get_dict(self):
        """Returns event info in dict form."""
        return self._asdict()

    dict = property(get_dict)
