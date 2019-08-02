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
import json
import requests_mock
import app


class TestServe(unittest.TestCase):
    @patch('app.requests')
    def test_auth_json(self, mock_requests):
        """Checks if users service returns a correctly formatted object.

        A dictionary with a boolean 'edit_access' field should be received.
        """
        mock_response = unittest.mock.MagicMock()
        mock_requests.post.return_value = mock_response
        mock_response.json.return_value = {"edit_access": True}

        response = app.get_user_info('example_user', 'example_url')

        mock_requests.post.assert_called_with(
            'example_url', data={'user_id': 'example_user'})
        valid_response = response['edit_access'] is True
        self.assertTrue(valid_response)

    def test_edit_access(self):
        """Tests if edit access is correctly retrieved from a user dict."""
        has_access = {'edit_access': True}
        no_access = {'edit_access': False}
        self.assertTrue(app.has_edit_access(has_access))
        self.assertFalse(app.has_edit_access(no_access))

    @patch('app.os')
    def test_config_endpoints(self, mock_os):
        """Test retrieval of endpoint env vars when defined or not defined."""
        existing_endpoint = 'this endpoint exists!'
        example_endpoints = ['url1', 'url2']
        mock_os.environ.__contains__.return_value = True
        mock_os.environ.get.return_value = existing_endpoint
        app.config_endpoints(example_endpoints)
        self.assertEqual(app.app.config['url1'], existing_endpoint)
        self.assertEqual(app.app.config['url2'], existing_endpoint)

        mock_os.environ.__contains__.return_value = False
        with self.assertRaises(NameError):
            app.config_endpoints(['url3'])


class TestGetPosts(unittest.TestCase):
    """Test app.get_posts function with mock call to posts service."""

    def setUp(self):
        self.url = app.app.config["POSTS_ENDPOINT"]
        self.posts_dict = {"posts": ["these", "are", "fake", "posts"]}

    @requests_mock.Mocker()
    def test_get_posts_success(self, mock_requests):
        """Test that posts are retrieved successfully."""
        mock_requests.get(
            self.url, text=json.dumps(self.posts_dict), status_code=200)
        posts = app.get_posts()
        self.assertTrue(posts, self.posts_dict)

    @requests_mock.Mocker()
    def test_get_posts_fail(self, mock_requests):
        """Test that error is raised when posts cannot be retrieved."""
        mock_requests.get(self.url, text="Error message.", status_code=500)
        with self.assertRaises(RuntimeError):
            app.get_posts()


class TestGetEvents(unittest.TestCase):
    """Test app.get_events function with mock call to events service."""

    def setUp(self):
        self.url = app.app.config["EVENTS_ENDPOINT"]
        self.events_dict = {"events": ["these", "are", "fake", "events"]}

    @requests_mock.Mocker()
    def test_get_events_success(self, mock_requests):
        """Test that events are returned successfully."""
        mock_requests.get(
            self.url, text=json.dumps(self.events_dict), status_code=200)
        posts = app.get_events()
        self.assertTrue(posts, self.events_dict)

    @requests_mock.Mocker()
    def test_get_events_fail(self, mock_requests):
        """Test error is raised when events cannot be retrieved."""
        mock_requests.get(self.url, text="Error message.", status_code=500)
        with self.assertRaises(RuntimeError):
            app.get_events()


class TestIDList(unittest.Testcase):
    """Test creation of ID list."""


if __name__ == '__main__':
    unittest.main()
