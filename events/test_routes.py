"""Unit tests for events service HTTP routes."""

import unittest
from contextlib import contextmanager
from bson import json_util
import mongomock
from app import app, os, connect_to_mongodb

EXAMPLE_TIME = '2019-08-01 16:53:48'

VALID_REQUEST_INFO = {
    'event_name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'author_id': 'admin',
    'event_time': EXAMPLE_TIME}
INVALID_REQUEST_INFO_MISSING_ATTRIBUTE = {
    'event_name': 'invalid_event_missing',
    'description': 'This event is missing an author!',
    'event_time': EXAMPLE_TIME}

VALID_EVENT_NAME = 'valid_event'
VALID_DB_EVENT = {
    'name': VALID_EVENT_NAME,
    'description': 'This event is formatted correctly!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'created_at': EXAMPLE_TIME,
    'event_id': 'unique_event_id0'}
VALID_DB_EVENT_WITH_ID = {
    'name': 'different_event_name',
    'description': 'This event is formatted correctly too!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'created_at': EXAMPLE_TIME,
    'event_id': 'unique_event_id1'}


@contextmanager
def environ(env):
    """Temporarily set environment variables inside the context manager and
    fully restore previous environment afterwards
    """
    original_env = {key: os.getenv(key) for key in env}
    os.environ.update(env)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value


class TestUploadEventRoute(unittest.TestCase):
    """Test add events endpoint POST /v1/add."""

    def setUp(self):
        """Set up test client and mock DB."""
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_add_valid_event(self):
        """Test posting of valid event."""
        response = self.client.post('/v1/add', data=VALID_REQUEST_INFO)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(self.coll.count_documents({}), 1)

    def test_add_invalid_event(self):
        """Test posting of invalid event with missing attributes."""
        response = self.client.post(
            '/v1/add', data=INVALID_REQUEST_INFO_MISSING_ATTRIBUTE)
        self.assertEqual(response.status_code, 400)

        self.assertEqual(self.coll.count_documents({}), 0)

    def test_db_not_defined(self):
        """Test adding event when DB connection is undefined."""
        with environ(os.environ):
            if "MONGODB_URI" in os.environ:
                del os.environ["MONGODB_URI"]
            app.config["COLLECTION"] = connect_to_mongodb()
            response = self.client.post('/v1/add', data=VALID_REQUEST_INFO)
            self.assertEqual(response.status_code, 500)

            self.assertEqual(self.coll.count_documents({}), 0)


class TestGetEventsRoute(unittest.TestCase):
    """Test retrieve all events endpoint GET /v1/."""

    def setUp(self):
        """Set up test client and mock DB."""
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.fake_events = [
            VALID_DB_EVENT,
            VALID_DB_EVENT_WITH_ID
        ]

    def test_get_existing_events(self):
        """Test retrieving all events when valid events are added to the DB."""
        app.config["COLLECTION"].insert_many(self.fake_events)

        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), len(self.fake_events))
        self.assertEqual(data['num_events'], len(self.fake_events))

    def test_get_no_events(self):
        """Test retrieving all events when no events are in the DB."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), 0)
        self.assertEqual(data['num_events'], 0)

    def test_db_not_defined(self):
        """Test getting events when DB connection is undefined."""
        with environ(os.environ):
            if "MONGODB_URI" in os.environ:
                del os.environ["MONGODB_URI"]
            app.config["COLLECTION"] = connect_to_mongodb()
            response = self.client.get('/v1/')
            self.assertEqual(response.status_code, 500)


class TestSearchEventsRoute(unittest.TestCase):
    """Test searching for an event by name at endpoint GET /v1/."""

    def setUp(self):
        """Set up test client and seed mock DB."""
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.fake_events = [
            VALID_DB_EVENT,
            VALID_DB_EVENT_WITH_ID
        ]
        self.coll.insert_many(self.fake_events)

    def test_search_existing_event(self):
        "Search for an event that exists in the DB."
        response = self.client.get('/v1/search?name=' + VALID_EVENT_NAME)
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(data['events'][0]['name'], VALID_EVENT_NAME)
        self.assertEqual(len(data['events']), 1)
        self.assertEqual(data['num_events'], 1)

    def test_search_nonexisting_event(self):
        "Search for an event that doesn't exist in the DB."
        response = self.client.get('/v1/search?name=' + "nonexistent event")
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), 0)
        self.assertEqual(data['num_events'], 0)

    def test_search_malformatted_name(self):
        "Malformatted query when searching for events."
        response = self.client.get('/v1/search?bad_arg=' + "not allowed")
        self.assertEqual(response.status_code, 400)

    def test_db_not_defined(self):
        """Test getting events when DB connection is undefined."""
        with environ(os.environ):
            if "MONGODB_URI" in os.environ:
                del os.environ["MONGODB_URI"]
            app.config["COLLECTION"] = connect_to_mongodb()
            response = self.client.get('/v1/search?name=' + VALID_EVENT_NAME)
            self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
