"""Copyright 2019 The Knative Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_testing import TestCase
import app

EXAMPLE_USER = "app_user"

VALID_POST = {'event_id': 1, 'text': 'hello', 'files': 'file.txt'}
INVALID_POST = {'event_id': 1, 'files': 'file.txt'}

VALID_EVENT_FORM = {
    'event_name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'event_time': '7-30-2019'}
INVALID_EVENT_FORM = {
    'event_name': 'invalid_event_missing',
    'description': 'This event is missing an time!'}

EXAMPLE_POSTS = ['example', 'posts', 'list']
EXAMPLE_EVENTS = ['example', 'events', 'list']


class TestTemplateRoutes(TestCase):
    """Tests all pageserve endpoints that return page templates."""

    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def setUp(self):
        """Set up test client."""
        self.client = app.app.test_client()

    @patch('app.get_user', MagicMock(return_value=EXAMPLE_USER))
    @patch('app.has_edit_access', MagicMock(return_value=True))
    @patch('app.get_posts', MagicMock(return_value=EXAMPLE_POSTS))
    def test_index(self):
        """Checks index page is rendered correctly by GET /v1/."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

        self.assertContext('user', EXAMPLE_USER)
        self.assertContext('auth', True)
        self.assertContext('posts', EXAMPLE_POSTS)

    @patch('app.get_user', MagicMock(return_value=EXAMPLE_USER))
    @patch('app.has_edit_access', MagicMock(return_value=True))
    @patch('app.get_events', MagicMock(return_value=EXAMPLE_EVENTS))
    def test_show_events(self):
        """Checks sub-events page is rendered correctly by GET /v1/events."""
        response = self.client.get('/v1/events')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('events.html')

        self.assertContext('user', EXAMPLE_USER)
        self.assertContext('auth', True)
        self.assertContext('events', EXAMPLE_EVENTS)


class TestAddPostRoute(unittest.TestCase):
    """Tests adding posts at POST /v1/add_post."""

    def setUp(self):
        self.coll = mongomock.MongoClient().db.collection
        app.config["COLLECTION"] = self.coll
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_add_valid_post(self):
        """Tests adding a valid post."""

    def test_add_valid_post(self):
        """Tests adding an invalid post."""


class TestAddEventRoute(unittest.TestCase):
    """Tests adding events at POST /v1/add_event."""

    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()
        self.expected_url = app.app.config['EVENTS_ENDPOINT'] + 'add'

    @patch('app.get_user', MagicMock(return_value=EXAMPLE_USER))
    @patch('app.requests')
    def test_add_valid_event(self, mock_requests):
        """Tests adding a valid event."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.content = "Example success message"
        mock_requests.post.return_value = mock_response

        response = self.client.post('/v1/add_event', data=VALID_EVENT_FORM)

        expected_arg = dict(**VALID_EVENT_FORM, author_id=EXAMPLE_USER)
        mock_requests.post.assert_called_with(self.expected_url,
                                              data=expected_arg)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.decode(), "Example success message")

    @patch('app.get_user', MagicMock(return_value=EXAMPLE_USER))
    @patch('app.requests')
    def test_add_invalid_event(self, mock_requests):
        """Tests adding an invalid event."""
        mock_response = MagicMock()
        mock_response.content = "Example error message"
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response

        response = self.client.post('/v1/add_event', data=INVALID_EVENT_FORM)

        expected_arg = dict(**INVALID_EVENT_FORM, author_id=EXAMPLE_USER)
        mock_requests.post.assert_called_with(self.expected_url,
                                              data=expected_arg)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), "Example error message")


if __name__ == '__main__':
    unittest.main()
