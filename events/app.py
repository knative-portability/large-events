import os
import datetime
import json
import pymongo
from bson import json_util

from flask import Flask, request, Response
from eventclass import Event

app = Flask(__name__)


class DBNotConnectedError(EnvironmentError):
    """Raised when not able to connect to the db."""


def connect_to_mongodb():
    # TODO(cmei4444): restructure to be consistent with other services
    # TODO(cmei4444): test with deployed service
    """Connects to MongoDB Atlas database.

    Returns events collection if connection is successful, and None otherwise.
    """
    class Thrower():  # pylint: disable=too-few-public-methods
        """Used to raise an exception on failed db connect."""

        def __getattribute__(self, _):
            raise DBNotConnectedError(
                "Not able to find MONGODB_URI environment variable")

    mongodb_uri = os.environ.get("MONGODB_URI")
    if mongodb_uri is None:
        return Thrower()  # not able to find db config var
    return pymongo.MongoClient(mongodb_uri).eventsDB.all_events


EVENTS_COLL = connect_to_mongodb()  # None if can't connect


@app.route('/v1/add', methods=['POST'])
def add_event():
    # TODO(cmei4444): Get event information from request data
    info = request.form['info']
    # TODO(cmei4444): Verify that user has event editing access
    current_time = datetime.datetime.now()
    info = build_event_info(info, current_time)
    try:
        event = Event(**info)
    except ValueError:      # missing or extra event attributes
        return Response(
            status=400,
            response="Event info was entered incorrectly.",
        )
    try:
        EVENTS_COLL.insert_one(event.dict)
        return Response(
            status=201,
        )
    except DBNotConnectedError as e:
        return Response(
            status=500,
            response="Events database was undefined.",
        )


def build_event_info(info, time):
    """Adds created_at time to event info dict."""
    return {**info, 'created_at': time}


@app.route('/v1/edit/<event_id>', methods=['PUT'])
def edit_event(event_id):
    """Edit the event with the given id."""
    pass


@app.route('/v1/', methods=['GET'])
def get_all_events():
    """Return a list of all events currently in the DB."""
    try:
        events = EVENTS_COLL.find()
        events = [Event(**ev).dict for ev in events]
        events_dict = build_events_dict(events)
        # TODO(cmei4444): test with pageserve to make sure the json format is
        # correct in the response
        # handle objects from MongoDB (e.g. ObjectID) that aren't JSON
        # serializable
        return json.loads(json_util.dumps(events_dict))
    except DBNotConnectedError as e:
        return "Events database was undefined.", 500


def build_events_dict(events):
    """Builds a dict in the correct format for returning through a GET request.

    Takes in a mongoDB cursor from querying the DB.
    """
    events_list = list(events)
    num_events = len(events_list)
    return {'events': events_list, 'num_events': num_events}


@app.route('/v1/search', methods=['GET'])
def search_event():
    """Search for the event with the given name in the DB."""
    pass


@app.route('/v1/<event_id>', methods=['PUT'])
def get_one_event(event_id):
    """Retrieve one event by event_id."""
    pass


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
