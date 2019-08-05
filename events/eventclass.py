"""Class to represent events."""

# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import namedtuple

EVENT_ATTRIBUTES = [
    'event_id',
    'name',
    'description',
    'author',
    'created_at',
    'event_time']


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
            elif getattr(self, att) != getattr(other, att):
                return False
        return True

    def get_dict(self):
        """Returns event info in dict form.

        Usually used to insert event info into the dictionary, so this converts
        the field event_id into _id to correspond with the MongoDB _id field.
        """
        info = self._asdict()
        if info['event_id']:    # only create _id field if event_id is not None
            info['_id'] = info['event_id']
            del info['event_id']
        return info

    dict = property(get_dict)
