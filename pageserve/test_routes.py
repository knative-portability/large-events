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


if __name__ == '__main__':
    unittest.main()
