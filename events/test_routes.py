import unittest
from unittest.mock import patch
import datetime
from bson import json_util
import mongomock
from app import app
from eventclass import Event

EXAMPLE_TIME = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)

VALID_REQUEST_INFO = {
    'event_name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'author_id': 'admin',
    'event_time': EXAMPLE_TIME}
VALID_REQUEST_INFO_DIFFERENT = {
    'event_name': 'different_valid_event',
    'description': 'This event is formatted correctly too!',
    'author_id': 'admin',
    'event_time': EXAMPLE_TIME}
INVALID_REQUEST_INFO_MISSING_ATTRIBUTE = {
    'event_name': 'invalid_event_missing',
    'description': 'This event is missing an author!',
    'event_time': EXAMPLE_TIME}

VALID_DB_EVENT = {
    'name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'created_at': EXAMPLE_TIME,
    'event_id': 'unique_event_id0'}
VALID_DB_EVENT_WITH_ID = {
    'name': 'test_event',
    'description': 'This event is formatted correctly too!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'created_at': EXAMPLE_TIME,
    'event_id': 'unique_event_id1'}

FAKE_INFO = [
    VALID_REQUEST_INFO,
]

FAKE_EVENTS = [
    VALID_DB_EVENT,
    VALID_DB_EVENT_WITH_ID
]


class TestUploadEventRoute(unittest.TestCase):
    """Test add events endpoint POST /v1/add."""
    def setUp(self):
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_event(self):
        """Test posting of event."""
        # TODO(cmei4444): test once retrieving form info is implemented


class TestGetEventsRoute(unittest.TestCase):
    """Test retrieve all events endpoint GET /v1/."""
    def setUp(self):
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_existing_events(self):
        """Test retrieving all events from /v1/ endpoint."""
        app.config["COLLECTION"].insert_many(FAKE_EVENTS)

        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['num_events'], 2)

    def test_get_no_events(self):
        """Test retrieving all events from /v1/ endpoint."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), 0)
        self.assertEqual(data['num_events'], 0)
