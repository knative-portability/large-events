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
from unittest.mock import patch
from flask import Flask
from flask_testing import TestCase
from app import app


class TestRoutes(TestCase):
    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def setUp(self):
        """Set up test client."""
        self.client = app.test_client()

    def test_index(self):
        """Check that index page is rendered correctly."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)

    def test_show_events(self):
        """Check that sub-events page is rendered correctly."""
        response = self.client.get('/v1/events')
        self.assertEqual(response.status_code, 200)
