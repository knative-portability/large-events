"""Unit tests for pageserve serving helper functions."""

# Authors: cmei4444
# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest
from unittest import mock
import requests
import requests_mock
import flask
import app

AUTHORIZED_RESPONSE_JSON = {'is_organizer': True}
UNAUTHORIZED_RESPONSE_JSON = {'is_organizer': False}

VALID_SESSION = {
    'user_id': 'abc123 pretend I am a user ID.',
    'name': 'Boaty McBoatface',
    'gauth_token': 'Pretend I am a valid GAuth token.'}


class TestServe(unittest.TestCase):
    """Test helper functions in pageserve app."""

    def setUp(self):
        """Create secret key for test session."""
        app.app.secret_key = 'Secret test key!'

    def test_get_user(self):
        """Checks if users service returns a correctly formatted object.

        Expects a user dictionary with a boolean 'is_organizer' field.
        This test mocks app.authenticate_with_users_service() to always
        return the response of an authenticated user that is authorized.
        """
        with app.app.test_request_context(), app.app.test_client():
            mock_response = mock.MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {'is_organizer': True}
            with mock.patch('app.authenticate_with_users_service',
                            return_value=mock_response):
                flask.session['user_id'] = VALID_SESSION['user_id']
                flask.session['name'] = VALID_SESSION['name']
                flask.session['gauth_token'] = VALID_SESSION['gauth_token']
                result = app.get_user()

                valid_response = result['is_organizer'] is True
                self.assertTrue(valid_response)

                # now test no user in session
                flask.session.clear()
                result = app.get_user()
                self.assertIsNone(result)

    def test_get_user_connection_error(self):
        """Can't connect to users service, requests raises, return None."""
        with app.app.test_request_context(), app.app.test_client(), \
                mock.patch('app.requests.post',
                           side_effect=requests.exceptions.ConnectionError):
            flask.session["gauth_token"] = VALID_SESSION["gauth_token"]
            self.assertIsNone(app.get_user())

    @requests_mock.Mocker()
    def test_is_organizer(self, requests_mocker):
        """Tests if authorization is correctly retrieved from users service.

        This test mocks away requests to the users service which is normally
        called by app.is_organizer.
        """
        # is authorized
        requests_mocker.post(app.app.config['USERS_ENDPOINT'] + 'authorization',
                             json=AUTHORIZED_RESPONSE_JSON)
        self.assertTrue(app.is_organizer(
            {'user_id': 'Pretend I am authorized.'}))
        # not authorized
        requests_mocker.post(app.app.config['USERS_ENDPOINT'] + 'authorization',
                             json=UNAUTHORIZED_RESPONSE_JSON)
        self.assertFalse(app.is_organizer(
            {'user_id': 'Pretend I am NOT authorized.'}))
        # No user sent give no authorization. This might happens when a user
        # is logged out so app.get_user() returns None.
        self.assertFalse(app.is_organizer(None))

    @mock.patch('app.os')
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
        self.url = app.app.config['POSTS_ENDPOINT']
        self.posts_dict = {'posts': ['these', 'are', 'fake', 'posts']}

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
        mock_requests.get(self.url, text='Error message.', status_code=500)
        with self.assertRaises(RuntimeError):
            app.get_posts()


class TestGetEvents(unittest.TestCase):
    """Test app.get_events function with mock call to events service."""

    def setUp(self):
        self.url = app.app.config['EVENTS_ENDPOINT']
        self.events_dict = {'events': ['these', 'are', 'fake', 'events']}

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
        mock_requests.get(self.url, text='Error message.', status_code=500)
        with self.assertRaises(RuntimeError):
            app.get_events()


if __name__ == '__main__':
    unittest.main()
