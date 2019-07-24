import unittest
from unittest.mock import patch
import mongomock
import app


class TestUploadEventRoute(unittest.TestCase):
    """Test add events endpoint POST /v1/add."""
    def setUp(self):
        app.config["COLLECTION"] = mongomock.MongoClient.db.collection
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_event(self):
        """Test posting of event."""


class TestGetEventsRoute(unittest.TestCase):
    """Test retrieve all events endpoint GET /v1/."""
    def setUp(self):
        app.config["COLLECTION"] = mongomock.MongoClient.db.collection
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_all(self):
        """Test retrieving all events from /v1/ endpoint."""
