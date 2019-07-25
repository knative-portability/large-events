"""Unit tests for events service HTTP routes."""

import unittest
from unittest.mock import patch
import datetime
from bson import json_util
import mongomock
from app import app
from eventclass import Event

EXAMPLE_TIME = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)

VALID_INFO = {
    'name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME}
VALID_INFO_WITH_ID = {
    'name': 'test_event',
    'description': 'This event is formatted correctly too!',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'event_id': "unique_event_id"}
INVALID_INFO_MISSING_ATTRIBUTE = {
    'name': 'invalid_event_missing',
    'description': 'This event is missing an author!',
    'event_time': EXAMPLE_TIME}
INVALID_INFO_EXTRA_ATTRIBUTE = {
    'name': 'invalid_event_extra',
    'description': 'This event has an extra attribute.',
    'author': 'admin',
    'event_time': EXAMPLE_TIME,
    'extra_attribute': 'I am invalid'}

FAKE_INFO = [
    VALID_INFO,
    VALID_INFO_WITH_ID
]


class TestUploadEventRoute(unittest.TestCase):
    """Test add events endpoint POST /v1/add."""
    def setUp(self):
        """Set up test client and mock DB."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_event(self):
        """Test posting of event."""
        # TODO(cmei4444): test once retrieving form info is implemented


class TestGetEventsRoute(unittest.TestCase):
    """Test retrieve all events endpoint GET /v1/."""
    def setUp(self):
        """Set up test client and mock DB."""
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.FAKE_EVENTS = [
            {**VALID_INFO, 'created_at': EXAMPLE_TIME, 'event_id': None},
            {**VALID_INFO_WITH_ID, 'created_at': EXAMPLE_TIME}
        ]

    def test_get_existing_events(self):
        """Test retrieving all events when valid events are added to the DB."""
        app.config["COLLECTION"].insert_many(self.FAKE_EVENTS)

        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), len(self.FAKE_EVENTS))
        self.assertEqual(data['num_events'], len(self.FAKE_EVENTS))

    def test_get_no_events(self):
        """Test retrieving all events when no events are in the DB."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        data = json_util.loads(response.data)

        self.assertEqual(len(data['events']), 0)
        self.assertEqual(data['num_events'], 0)
