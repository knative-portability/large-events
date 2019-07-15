import os
import logging
import datetime
import pymongo

from collections import namedtuple
from flask import Flask, request, Response

app = Flask(__name__)


def connect_to_mongodb():
    """Connects to MongoDB Atlas database.

    Returns events collection if connection is successful, and None otherwise.
    """
    mongodb_uri = os.environ.get("MONGODB_URI")
    if mongodb_uri is None:
        print("Alert: not able to find MONGODB_URI environmental variable, "
              "no connection to MongoDB instance")
        return None  # not able to find db config var
    return pymongo.MongoClient(mongodb_uri).eventsDB.all_events


EVENTS_COLL = connect_to_mongodb()  # None if can't connect


@app.route('/v1/add', methods=['POST'])
def add_event():
    # TODO(cmei4444): Get event information from request data
    info = request.form['info']
    # TODO(cmei4444): Verify that user has event editing access
    current_time = datetime.datetime.now()
    build_event_info(info, current_time)
    try:
        event = Event(info)
    except ValueError:      # missing or extra event attributes
        return Response(
            status=400,
            response="Event info was entered incorrectly.",
        )
    if EVENTS_COLL is not None:
        event.add_to_db(EVENTS_COLL)
    else:
        return Response(
            status=500,
            response="Database was undefined.",
        )
    return Response(
        status=201,
    )


def build_event_info(info, time):
    """Adds created_at time to event info dict."""
    info['created_at'] = time
    return info


@app.route('/v1/edit/<event_id>', methods=['PUT'])
def edit_event(event_id):
    """Edit the event with the given id."""
    pass


@app.route('/v1/', methods=['GET'])
def get_all_events():
    """Return a list of all events currently in the DB."""
    pass


@app.route('/v1/search', methods=['GET'])
def search_event():
    """Search for the event with the given name in the DB."""
    pass


@app.route('/v1/<event_id>', methods=['PUT'])
def get_one_event(event_id):
    """Retrieve one event by event_id."""
    pass


def equal_times(time_1, time_2):
    """Determines if two times are equal.

    Times can be represented as strings (mainly for testing) or as
    datetime.datetime objects. Datetime objects are rounded to the nearest
    millisecond before comparison.

    Used for comparing Event objects, since MongoDB truncates times to the
    nearest millisecond.
    """
    if isinstance(time_1, type(time_2)):
        if isinstance(time_1, datetime.datetime):
            time_1 = time_1.replace(
                microsecond=(time_1.microsecond // 1000) * 1000)
            time_2 = time_2.replace(
                microsecond=(time_2.microsecond // 1000) * 1000)
        return time_1 == time_2
    return False


EVENT_ATTRIBUTES = [
    'event_id',
    'name',
    'description',
    'author',
    'created_at',
    'event_time']


class Event(namedtuple("EventTuple", EVENT_ATTRIBUTES)):
    # TODO(cmei4444): move Event class to a separate file for better
    # code organization
    def __new__(cls, info):
        """Constructs an event object represented by a EventTuple namedtuple.

        Raises a ValueError if any attributes are missing or if extra
        attributes are included.
        """
        if "event_id" not in info:
            info['event_id'] = None
        if '_id' in info:       # found DB-generated ID, override given one
            info['event_id'] = info['_id']
            del info['_id']
        self = super(Event, cls).__new__(cls, **info)
        return self

    def __eq__(self, other):
        """Determines if two events have the same info, excluding event_id."""
        if not isinstance(other, Event):
            return False
        for att in EVENT_ATTRIBUTES:
            if att == 'event_time' or att == 'created_at':
                if not equal_times(getattr(self, att), getattr(other, att)):
                    print('times not eq')
                    return False
            elif att != 'event_id' and (
                    getattr(self, att) != getattr(other, att)):
                return False
        return True

    def add_to_db(self, events_collection):
        """Adds the event to the specified collection."""
        # TODO(cmei4444): move out of class
        events_collection.insert_one(self._asdict())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
