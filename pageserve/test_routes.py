"""Unit tests for pageserve service HTTP routes."""

# Authors: mukobi
# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import patch, MagicMock
import ast
import requests_mock
from flask_testing import TestCase
import flask
from flask import url_for
import app

VALID_SESSION = {
    'user_id': '42',
    'name': 'Ford Prefect',
    'gauth_token': 'I am a pretend token'}
ERROR_BAD_TOKEN_TEXT = 'Error: bad gauth_token.'
ERROR_BAD_TOKEN_STATUS = 400
VALID_USER_AUTH_STATUS = 201

AUTHORIZED_USER_OBJECT = {
    'user_id': 'app_user',
    'name': 'app_user',
    'is_organizer': True}
NOT_AUTHORIZED_USER_OBJECT = {
    'user_id': 'app_user',
    'name': 'app_user',
    'is_organizer': False}

VALID_POST_FORM = {
    'event_id': 'valid_post_id',
    'text': 'This event is valid.',
    'file_1': 'fake_file_1.txt',
    'file_2': 'fake_file_2.txt'}
INVALID_POST_FORM = {
    'event_id': 'invalid_post_id'}

VALID_EVENT_FORM = {
    'event_name': 'valid_event',
    'description': 'This event is formatted correctly!',
    'event_time': '7-30-2019'}
INVALID_EVENT_FORM = {
    'event_name': 'invalid_event_missing',
    'description': 'This event is missing a time!'}

EXAMPLE_EVENT_ID = '123456789123456789123456'
EXAMPLE_POSTS = [
    {'_id': {'$oid': '123abc'},
     'event_id': EXAMPLE_EVENT_ID,
     'text': 'example post 1.'},
    {'_id': {'$oid': '456def'},
     'event_id': EXAMPLE_EVENT_ID,
     'text': 'example post 2.'}]

DIFFERENT_EVENT_ID = '987654321987654321654321'
EXAMPLE_EVENTS = [
    {'_id': EXAMPLE_EVENT_ID,
     'name': 'valid_event',
     'description': 'this event is valid',
     'event_time': 'soon',
     'author': 'app_user',
     'created_at': 'in the past'},
    {'_id': DIFFERENT_EVENT_ID,
     'name': 'valid_event',
     'description': 'this event is valid too',
     'event_time': 'soon',
     'author': 'app_user',
     'created_at': 'in the past'}]


class TestAuthenticateAndGetUser(unittest.TestCase):
    """Test authentication endpoint POST /v1/authenticate."""

    def assert_sessions_are_equal(self, first, second):
        """Asserts the two sessions are the same.

        Only compares the 'user_id' and 'name' fields, but ignores the
        'gauth_token' field which is not returned from the users service
        but is stored in the session by app.authenticate_with_users_service.
        """
        self.assertEqual(first['user_id'], second['user_id'])
        self.assertEqual(first['name'], second['name'])

    def setUp(self):
        """Set up test client."""
        app.app.config['TESTING'] = True  # propagate exceptions to test client
        app.app.secret_key = 'Dummy key used for testing the flask session'

    @requests_mock.Mocker()
    def test_valid_authentication(self, requests_mocker):
        """GAuth token successfully authenticates."""
        with app.app.test_request_context(), app.app.test_client() as client:
            requests_mocker.post(app.app.config['USERS_ENDPOINT'] + 'authenticate',
                                 json=VALID_SESSION,
                                 status_code=VALID_USER_AUTH_STATUS)
            result = client.post('/v1/authenticate', data={
                'gauth_token': 'I do not matter because requests is mocked'})
            self.assertEqual(result.status_code, VALID_USER_AUTH_STATUS)
            result_dict = ast.literal_eval(result.data.decode())
            self.assert_sessions_are_equal(
                result_dict, VALID_SESSION)
            # user stored in session
            self.assertEqual(len(flask.session), len(VALID_SESSION))
            self.assert_sessions_are_equal(
                flask.session, VALID_SESSION)

    @requests_mock.Mocker()
    def test_failed_authentication(self, requests_mocker):
        """GAuth token fails authentication."""
        with app.app.test_request_context(), app.app.test_client() as client:
            requests_mocker.post(app.app.config['USERS_ENDPOINT'] + 'authenticate',
                                 text=ERROR_BAD_TOKEN_TEXT,
                                 status_code=ERROR_BAD_TOKEN_STATUS)
            result = client.post('/v1/authenticate', data={
                'gauth_token': 'I do not matter because requests is mocked'})
            self.assertEqual(result.status_code, ERROR_BAD_TOKEN_STATUS)
            self.assertEqual(result.data.decode(), ERROR_BAD_TOKEN_TEXT)
            # user not stored in session
            self.assertEqual(len(flask.session), 0)
            self.assertNotIn('user_id', flask.session)

    def test_no_token_given(self):
        """Failed to provide a GAuth token to authenticate."""
        with app.app.test_request_context(), app.app.test_client() as client:
            result = client.post('/v1/authenticate')
            self.assertEqual(result.status_code, 400)
            self.assertIn('Error', result.data.decode())
            # nothing stored in session
            self.assertEqual(len(flask.session), 0)


class TestSignOut(unittest.TestCase):
    """Test sign out endpoint GET /v1/sign_out."""

    def setUp(self):
        """Set up test client."""
        app.app.config['TESTING'] = True  # propagate exceptions to test client
        app.app.secret_key = 'Dummy key used for testing the flask session'

    def test_was_logged_in(self):
        """Sign out a user that was logged in (usual behaviour)."""
        with app.app.test_request_context(), app.app.test_client() as client:
            flask.session['user_id'] = VALID_SESSION['user_id']
            flask.session['name'] = VALID_SESSION['name']
            flask.session['gauth_token'] = VALID_SESSION['gauth_token']
            # user in session before
            self.assertIn('user_id', flask.session)
            self.assertEqual(len(flask.session), len(VALID_SESSION))
            result = client.get(
                '/v1/sign_out')
            # empty session after
            self.assertNotIn('user_id', flask.session)
            self.assertEqual(len(flask.session), 0)
            # check for redirect to index
            self.assertEqual(result.status_code, 302)
            with app.app.test_request_context():
                self.assertTrue(
                    result.headers['location'].endswith(url_for('index')))

    def test_was_not_logged_in(self):
        """Try to sign out a user that was not logged in."""
        with app.app.test_request_context(), app.app.test_client() as client:
                # empty session before
            self.assertNotIn('user_id', flask.session)
            self.assertEqual(len(flask.session), 0)
            result = client.get(
                '/v1/sign_out')
            # empty session after
            self.assertNotIn('user_id', flask.session)
            self.assertEqual(len(flask.session), 0)
            # check for redirect to index
            self.assertEqual(result.status_code, 302)
            with app.app.test_request_context():
                self.assertTrue(
                    result.headers['location'].endswith(url_for('index')))


class TestMainTemplateRoutes(TestCase):
    """Tests pageserve endpoints that return the core page templates."""

    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        test_app = flask.Flask(__name__)
        test_app.config['TESTING'] = True
        return test_app

    def setUp(self):
        """Set up test client."""
        self.client = app.app.test_client()

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @patch('app.get_posts', MagicMock(return_value=EXAMPLE_POSTS))
    def test_index(self):
        """Checks index page is rendered correctly by GET /v1/."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

        self.assertContext('auth', True)
        self.assertContext('posts', EXAMPLE_POSTS)
        self.assertContext('app_config', app.app.config)

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @patch('app.get_posts', MagicMock(side_effect=RuntimeError))
    def test_index_posts_fail(self):
        """Checks GET /v1/ response when posts cannot be retrieved."""
        response = self.client.get('/v1/')
        self.assertEqual(response.status_code, 500)

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @patch('app.get_events', MagicMock(return_value=EXAMPLE_EVENTS))
    def test_show_events(self):
        """Checks sub-events page is rendered correctly by GET /v1/events."""
        response = self.client.get('/v1/events')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('events.html')

        self.assertContext('auth', True)
        self.assertContext('events', EXAMPLE_EVENTS)
        self.assertContext('app_config', app.app.config)

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @patch('app.get_events', MagicMock(side_effect=RuntimeError))
    def test_index_events_fail(self):
        """Checks GET /v1/events response when events cannot be retrieved."""
        response = self.client.get('/v1/events')
        self.assertEqual(response.status_code, 500)


class TestSearchEventsRoute(TestCase):
    """Tests searching for events at POST /v1/search_event."""

    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        test_app = flask.Flask(__name__)
        test_app.config['TESTING'] = True
        return test_app

    def setUp(self):
        """Set up test client."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()
        self.expected_url = app.app.config['EVENTS_ENDPOINT'] + 'search'

    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_search_existing_events(self, mock_requests):
        """Test searching for existing events."""
        mock_requests.get(self.expected_url,
                          json={'events': EXAMPLE_EVENTS,
                                'num_events': len(EXAMPLE_EVENTS)},
                          status_code=200)
        query = {'event_name': 'valid_event'}
        response = self.client.post('/v1/search_event', data=query)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('search_results.html')

        self.assertContext('auth', True)
        self.assertContext('events', EXAMPLE_EVENTS)
        self.assertContext('app_config', app.app.config)

    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_search_no_events_found(self, mock_requests):
        """Test searching for nonexisting events."""
        mock_requests.get(self.expected_url,
                          json={'events': [], 'num_events': 0},
                          status_code=200)
        query = {'event_name': 'nonexistent_event'}
        response = self.client.post('/v1/search_event', data=query)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('search_results.html')

        self.assertContext('auth', True)
        self.assertContext('events', [])
        self.assertContext('app_config', app.app.config)

    @requests_mock.Mocker()
    def test_search_events_error(self, mock_requests):
        """Test events service error when searching for events."""
        mock_requests.get(self.expected_url,
                          text='Error in getting events',
                          status_code=500)
        query = {'event_name': 'valid_event'}
        response = self.client.post('/v1/search_event', data=query)

        self.assertEqual(response.status_code, 500)

    @requests_mock.Mocker()
    def test_malformatted_search(self, mock_requests):
        """Test searching without required event_name field."""
        response = self.client.post('/v1/search_event')

        self.assertEqual(response.status_code, 400)


class TestQueryEventsByIDRoute(TestCase):
    """Tests querying for events at GET /v1/query_event."""
    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        test_app = flask.Flask(__name__)
        test_app.config['TESTING'] = True
        return test_app

    def setUp(self):
        """Set up test client."""
        # app.app.config["TESTING"] = True
        self.client = app.app.test_client()
        self.expected_url = app.app.config['EVENTS_ENDPOINT']

    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_query_existing_event(self, mock_requests):
        """Test querying for existing event."""
        mock_requests.put(self.expected_url + EXAMPLE_EVENT_ID,
                          json={'events': EXAMPLE_EVENTS[0], 'num_events': 1},
                          status_code=200)
        query = {'event_id': EXAMPLE_EVENT_ID}
        response = self.client.get('/v1/query_event', query_string=query)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('search_results.html')

        self.assertContext('auth', True)
        self.assertContext('events', EXAMPLE_EVENTS[0])
        self.assertContext('app_config', app.app.config)

    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_query_no_event_found(self, mock_requests):
        """Test querying for nonexisting event."""
        nonexistent_id = 'nonexistent1234567890123'
        mock_requests.put(self.expected_url + nonexistent_id,
                          json={'events': [], 'num_events': 0},
                          status_code=200)
        query = {'event_id': nonexistent_id}
        response = self.client.get('/v1/query_event', query_string=query)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('search_results.html')

        self.assertContext('auth', True)
        self.assertContext('events', [])
        self.assertContext('app_config', app.app.config)

    @requests_mock.Mocker()
    def test_query_events_error(self, mock_requests):
        """Test events service error when querying for events."""
        mock_requests.put(self.expected_url + EXAMPLE_EVENT_ID,
                          text='Error in getting events',
                          status_code=500)
        query = {'event_id': EXAMPLE_EVENT_ID}
        response = self.client.get('/v1/query_event', query_string=query)

        self.assertEqual(response.status_code, 500)

    @requests_mock.Mocker()
    def test_malformatted_query(self, mock_requests):
        """Test querying without required event_id field."""
        response = self.client.get('/v1/query_event')

        self.assertEqual(response.status_code, 400)


@patch('app.is_organizer', MagicMock(return_value=True))
@patch('app.get_events', MagicMock(return_value=EXAMPLE_EVENTS))
class TestGetPostsForEventRoute(TestCase):
    """Tests retrieving posts for an event at GET /v1/get_posts/<event_id>."""

    def create_app(self):
        """Creates and returns a Flask instance.

        Required by flask_testing to test templates."""
        test_app = flask.Flask(__name__)
        test_app.config['TESTING'] = True
        return test_app

    def setUp(self):
        """Set up test client."""
        self.client = app.app.test_client()
        self.expected_url = app.app.config['POSTS_ENDPOINT'] + 'by_event/'

    @requests_mock.Mocker()
    def test_get_existing_posts(self, mock_requests):
        """Checks existing posts are returned correctly."""
        mock_requests.get(self.expected_url + EXAMPLE_EVENT_ID,
                          json={'events': EXAMPLE_POSTS,
                                'num_events': len(EXAMPLE_POSTS)},
                          status_code=200)
        response = self.client.get(f'/v1/get_posts/{EXAMPLE_EVENT_ID}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

        self.assertContext('auth', True)
        self.assertContext('posts', EXAMPLE_POSTS)
        self.assertContext('app_config', app.app.config)

    @requests_mock.Mocker()
    def test_get_nonexistent_posts(self, mock_requests):
        """Checks the case when no posts are found."""
        mock_requests.get(self.expected_url + DIFFERENT_EVENT_ID,
                          json={'events': [], 'num_events': 0},
                          status_code=200)
        response = self.client.get(f'/v1/get_posts/{DIFFERENT_EVENT_ID}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

        self.assertContext('auth', True)
        self.assertContext('posts', [])
        self.assertContext('app_config', app.app.config)

    @requests_mock.Mocker()
    def test_posts_service_error(self, mock_requests):
        """Checks the case when posts service throws an error."""
        mock_requests.get(self.expected_url + EXAMPLE_EVENT_ID,
                          status_code=500)
        response = self.client.get(f'/v1/get_posts/{EXAMPLE_EVENT_ID}')
        self.assertEqual(response.status_code, 500)


class TestAddPostRoute(unittest.TestCase):
    """Tests adding posts at POST /v1/add_post."""

    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        self.expected_url = app.app.config['POSTS_ENDPOINT'] + 'add'

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @requests_mock.Mocker()
    def test_add_valid_post(self, mock_requests):
        """Tests adding a valid post."""
        mock_requests.post(app.app.config['POSTS_ENDPOINT'] + 'add',
                           text='Example success message',
                           status_code=201)

        response = self.client.post('/v1/add_post', data=VALID_POST_FORM)

        # check for redirect to index
        self.assertEqual(response.status_code, 302)
        with app.app.test_request_context():
            self.assertTrue(
                response.headers['location'].endswith(url_for('index')))

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @requests_mock.Mocker()
    def test_add_invalid_post(self, mock_requests):
        """Tests adding an invalid post."""
        mock_requests.post(app.app.config['POSTS_ENDPOINT'] + 'add',
                           text='Example error message',
                           status_code=400)

        response = self.client.post('/v1/add_post', data=INVALID_POST_FORM)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), 'Example error message')

    def test_not_logged_in(self):
        """Not logged in, don't add."""
        response = self.client.post('/v1/add_post', data=VALID_POST_FORM)

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error:", response.data.decode())


class TestAddEventRoute(unittest.TestCase):
    """Tests adding events at POST /v1/add_event."""

    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        self.expected_url = app.app.config['EVENTS_ENDPOINT'] + 'add'

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_add_valid_event(self, mock_requests):
        """Tests adding a valid event."""
        mock_requests.post(app.app.config['EVENTS_ENDPOINT'] + 'add',
                           text='Example success message',
                           status_code=201)

        response = self.client.post('/v1/add_event', data=VALID_EVENT_FORM)

        # check for redirect to index
        self.assertEqual(response.status_code, 302)
        with app.app.test_request_context():
            self.assertTrue(
                response.headers['location'].endswith(url_for('index')))

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_add_invalid_event(self, mock_requests):
        """Tests adding an invalid event."""
        mock_requests.post(app.app.config['EVENTS_ENDPOINT'] + 'add',
                           text='Example error message',
                           status_code=400)

        response = self.client.post('/v1/add_event', data=INVALID_EVENT_FORM)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.data.decode())

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @patch('app.is_organizer', MagicMock(return_value=True))
    @requests_mock.Mocker()
    def test_error_at_events_service(self, mock_requests):
        """Events service doesn't like what we give it."""
        mock_requests.post(app.app.config['EVENTS_ENDPOINT'] + 'add',
                           text='Error: Example error message',
                           status_code=400)

        response = self.client.post('/v1/add_event', data=VALID_EVENT_FORM)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.data.decode())

    def test_not_authenticated(self):
        """Tests trying to add an event without authorization."""
        response = self.client.post('/v1/add_event', data=VALID_EVENT_FORM)

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error", response.data.decode())

    @patch('app.get_user', MagicMock(return_value=NOT_AUTHORIZED_USER_OBJECT))
    def test_not_authorized(self):
        """Tests trying to add an event without authorization."""
        response = self.client.post('/v1/add_event', data=VALID_EVENT_FORM)

        self.assertEqual(response.status_code, 403)
        self.assertIn("Error", response.data.decode())


class TestDeletePostRoute(unittest.TestCase):
    """Tests delete posts at DELETE /v1/delete_post/<post_id>."""

    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @requests_mock.Mocker()
    def test_valid_delete(self, mock_requests):
        """Happy case, authenticated and authorized to delete post."""
        post_id = 'abc123'
        mock_requests.delete(
            app.app.config['POSTS_ENDPOINT'] + post_id,
            text='Example success message', status_code=204)
        response = self.client.delete(
            f'/v1/delete_post/{post_id}')
        self.assertEqual(response.status_code, 204)

    def test_invalid_not_authenticated(self):
        """Not authenticated, i.e. get_user() returns None."""
        post_id = 'abc123'
        response = self.client.delete(
            f'/v1/delete_post/{post_id}')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Error', response.data.decode())

    @patch('app.get_user', MagicMock(return_value=AUTHORIZED_USER_OBJECT))
    @requests_mock.Mocker()
    def test_invalid_fails_on_posts_service(self, mock_requests):
        """Posts doesn't like the requests, e.g. author_id doesn't match."""
        post_id = 'abc123'
        mock_requests.delete(
            app.app.config['POSTS_ENDPOINT'] + post_id,
            text='Document not found.', status_code=404)
        response = self.client.delete(
            f'/v1/delete_post/{post_id}')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
