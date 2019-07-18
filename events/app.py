import os
import datetime
import pymongo

from flask import Flask, request, Response, json
from eventclass import Event

app = Flask(__name__)


def connect_to_mongodb():
    """Connects to MongoDB Atlas database.

    Returns events collection if connection is successful, and None otherwise.
    """
    class DBNotConnectedError(EnvironmentError):
        """Raised when not able to connect to the db."""

    class Thrower(object):
        """Used to raise an exception on failed db connect."""

        def __getattribute__(self, _):
            raise DBNotConnectedError(
                "Not able to find MONGODB_URI environmental variable")

    mongodb_uri = os.environ.get("MONGODB_URI")
    if mongodb_uri is None:
        return Thrower()  # DBNotConnectedErrorot able to find db config var
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
            response="Database was undefined.",
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
        events = events_collection.find()
        events_dict = build_events_dict(events)
        return Response(
            events_dict,
            status=200,
            mimetype='application/json'
        )
    except DBNotConnectedError as e:
        return Response(
            status=500,
            response="Database was undefined.",
        )


def build_events_dict(events):
    """Builds a dict in the correct format for returning through a GET request.

    Takes in a mongoDB cursor from querying the DB.
    """
    num_events = len(events)
    return {'events': list(events), 'num_events': num_events}


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
