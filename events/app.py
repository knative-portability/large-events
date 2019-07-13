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
    # MongoDB timestamp precision level, floor to milliseconds
    time -= datetime.timedelta(0, 0, time.microsecond % 1000)
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


attributes = [
    'event_id',
    'name',
    'description',
    'author',
    'created_at',
    'event_time']

EventTuple = namedtuple('EventTuple', attributes)


class Event(object):
    # TODO(cmei4444): move Event class to a separate file for better
    # code organization
    # TODO(cmei4444): implement as namedtuple with __new__ method
    def __init__(self, info):
        """Constructs an event object represented by a EventTuple namedtuple.

        Creating the EventTuple raises a ValueError if any attributes are
        missing or if extra attributes are included.
        """
        # event_id is defined by the database, not the user
        if "event_id" not in info:
            info['event_id'] = None
        if '_id' in info:       # found DB-generated ID, override given one
            info['event_id'] = info['_id']
            del info['_id']
        self.info = EventTuple(**info)

    def __eq__(self, other):
        """Determines if two events have the same info, excluding event_id."""
        if not isinstance(other, Event):
            return False
        for att in attributes:
            if att != 'event_id' and (
                    self.get_info()[att] != other.get_info()[att]):
                return False
            if att == 'event_time' or att == 'created_at':
                # TODO(cmei4444): ignore time error here instead of rounding
                # to the millisecond in build_event_info
                pass
        return True

    def add_to_db(self, events_collection):
        """Adds the event to the specified collection."""
        # TODO(cmei4444): move out of class
        events_collection.insert_one(self.get_info())

    def get_info(self):
        """Returns event info converted back into dictionary form.

        Used for inserting into the DB or serving through requests.
        """
        return self.info._asdict()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
