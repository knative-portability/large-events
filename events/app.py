import os
import logging
import datetime
import pymongo
# import pprint

from flask import Flask, request, Response

app = Flask(__name__)


def db_setup():
    """Connect to MongoDB Atlas database, returns events collection."""
    MONGODB_ATLAS_USERNAME = os.environ.get(
        "MONGODB_ATLAS_USERNAME")
    MONGODB_ATLAS_PASSWORD = os.environ.get(
        "MONGODB_ATLAS_PASSWORD")
    MONGODB_ATLAS_CLUSTER_ADDRESS = os.environ.get(
        "MONGODB_ATLAS_CLUSTER_ADDRESS")
    PYMONGO_URI = "mongodb+srv://{}:{}@{}".format(
        MONGODB_ATLAS_USERNAME,
        MONGODB_ATLAS_PASSWORD,
        MONGODB_ATLAS_CLUSTER_ADDRESS)
    # print("Pymongo URI: {}".format(PYMONGO_URI))
    client = pymongo.MongoClient(PYMONGO_URI)
    eventsDB = client.eventsDB
    return eventsDB.all_events


@app.route('/v1/add', methods=['POST'])
def add_event():
    # TODO(cmei4444): Get event information from request data
    info = request.form['info']
    current_time = datetime.datetime.now()
    build_event_info(info, current_time)
    event = Event(info)
    if not event.is_valid():
        return Response(
            status=400,
            response="Event info was entered incorrectly.",
        )

    event.add_to_db()
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


class Event(object):
    attributes = [
        'event_id',
        'name',
        'description',
        'author',
        'created_at',
        'event_time']

    def __init__(self, info):
        self.info = dict(info)
        # event_id is defined by the database, not the user
        if "event_id" not in self.info:
            self.info['event_id'] = None

    def __eq__(self, other):
        """Determines if two events have the same info, excluding event_id."""
        for att in self.attributes:
            if att != 'event_id' and (self.info[att] != other.info[att]):
                return False
        return True

    def is_valid(self):
        """Checks that all of the required attributes are in the event info."""
        for att in self.attributes:
            if att not in self.info:
                return False
        return True

    def add_to_db(self):
        """Adds the event to the database, returns added dict."""
        events_coll.insert_one(self.info)
        return self.info


if __name__ == "__main__":
    db_setup()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
