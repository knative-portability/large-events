"""Unit tests for users service HTTP routes."""

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
from unittest import mock
import json
import mongomock
import app

AUTHORIZED_USER_ID = 'authorized-user'
NON_AUTHORIZED_USER_ID = 'non-authorized-user'
MALFORMATTED_IN_DB_USER = 'this-user-has-no-"is_organizer"_db_field'
MISSING_USER = 'not-a-user-in-the-database'

FAKE_USERS = [
    {'user_id': AUTHORIZED_USER_ID,
     'name': AUTHORIZED_USER_ID,
     'is_organizer': True},
    {'user_id': NON_AUTHORIZED_USER_ID,
     'name': NON_AUTHORIZED_USER_ID,
     'is_organizer': False},
    {'user_id': MALFORMATTED_IN_DB_USER}]

IDINFO_VALID = {
    'iss': 'accounts.google.com',
    'sub': AUTHORIZED_USER_ID,
    'name': 'John Doe'}
IDINFO_INVALID_ISSUER = {
    'iss': 'malicious.site.net'}
IDINFO_MISSING_NAME = {
    'iss': 'accounts.google.com',
    'sub': 'I have an ID but no name'}
DUMMY_GAUTH_REQUEST_DATA = {'gauth_token': 'fake_token_0123'}

AUTHORIZED_UPDATER_ID = 'authorized-self-id'
AUTHORIZED_UPDATER = {
    'user_id': AUTHORIZED_UPDATER_ID,
    'name': AUTHORIZED_UPDATER_ID,
    'is_organizer': True}
NON_AUTHORIZED_UPDATER_ID = 'non-authorized-self-id'
NON_AUTHORIZED_UPDATER = {
    'user_id': NON_AUTHORIZED_UPDATER_ID,
    'name': NON_AUTHORIZED_UPDATER_ID,
    'is_organizer': False}
IDINFO_AUTHORIZED_UPDATER = {
    'iss': 'accounts.google.com',
    'sub': AUTHORIZED_UPDATER_ID,
    'name': 'John Doe'}
IDINFO_NON_AUTHORIZED_UPDATER = {
    'iss': 'accounts.google.com',
    'sub': NON_AUTHORIZED_UPDATER_ID,
    'name': 'Draco Malfo'}


class TestAuthenticateUser(unittest.TestCase):
    """Test authenticate user endpoint POST /v1/authenticate."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.app.config['COLLECTION'] = mongomock.MongoClient().db.collection
        app.app.config['TESTING'] = True  # propagate exceptions to test client
        self.client = app.app.test_client()
        # Patch google.oauth2.id_token
        patcher = mock.patch('app.id_token')
        self.verify_oauth2_token = patcher.start().verify_oauth2_token
        self.addCleanup(patcher.stop)

    def assert_equal_idinfos(self, response, fake):
        """Asserts if the 2 idinfo objects are the same.

        Based on the 'sub'/'user_id' and 'name' attributes.
        Note: 'sub' in the fake corresponds to 'user_id' in the real
        object from the response.
        """
        self.assertEqual(response['user_id'], fake['sub'])
        self.assertEqual(response['name'], fake['name'])

    def test_valid_token(self):
        """Simulate extracting a valid token."""
        self.verify_oauth2_token.return_value = IDINFO_VALID
        result = self.client.post(
            '/v1/authenticate', data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = json.loads(result.data)
        self.assert_equal_idinfos(response_body, IDINFO_VALID)
        self.assertEqual(result.status_code, 201)

    def test_missing_name(self):
        """User object missing name, perhaps from lack of permissions."""
        self.verify_oauth2_token.return_value = IDINFO_MISSING_NAME
        result = self.client.post(
            '/v1/authenticate', data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = result.data.decode()
        self.assertIn('Error', response_body)
        self.assertEqual(result.status_code, 400)

    def test_no_authentication_token(self):
        """No token provided."""
        result = self.client.post(
            '/v1/authenticate')
        response_body = result.data.decode()
        self.assertIn('Error', response_body)
        self.assertEqual(result.status_code, 400)

    def test_bad_issuer(self):
        """Bad token issuer(not Google Accounts)."""
        self.verify_oauth2_token.return_value = IDINFO_INVALID_ISSUER
        result = self.client.post(
            '/v1/authenticate', data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = result.data.decode()
        self.assertIn('Error', response_body)
        self.assertEqual(result.status_code, 400)

    def test_authentication_failed(self):
        """Authentication failed due to invalid token.

        This might occur when the token has expired, it's Google OAuth
        client ID does not match that of the server, or the token is
        otherwise invalid.
        """
        self.verify_oauth2_token.side_effect = ValueError('Bad token.')
        result = self.client.post(
            '/v1/authenticate', data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = result.data.decode()
        self.assertIn('Error', response_body)
        self.assertEqual(result.status_code, 400)


class TestGetAuthorization(unittest.TestCase):
    """Test get authorization endpoint POST /v1/authorization."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.app.config['COLLECTION'] = mongomock.MongoClient().db.collection
        app.app.config['COLLECTION'].insert_many(FAKE_USERS)
        app.app.config['TESTING'] = True  # propagate exceptions to test client
        self.client = app.app.test_client()

    def test_is_authorized(self):
        """Get authorization of authorized user."""
        result = self.client.post(
            '/v1/authorization', data={'user_id': AUTHORIZED_USER_ID})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {'is_organizer': True})

    def test_not_authorized(self):
        """Get authorization of non-authorized user."""
        result = self.client.post(
            '/v1/authorization', data={'user_id': NON_AUTHORIZED_USER_ID})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {'is_organizer': False})

    def test_malformatted_in_db(self):
        """Get authorization of user that is malformatted in the db."""
        result = self.client.post(
            '/v1/authorization', data={'user_id': MALFORMATTED_IN_DB_USER})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {'is_organizer': False})

    def test_missing_param(self):
        """Try to get authorization but don't supply user_id."""
        result = self.client.post('/v1/authorization')
        self.assertEqual(result.status_code, 400)


@mock.patch('app.get_user_from_gauth_token',
            mock.Mock(return_value=IDINFO_AUTHORIZED_UPDATER))
class TestUpdateAuthorization(unittest.TestCase):
    """Test update authorization endpoint POST /v1/authorization/update.

    Depends on app.find_authorization_in_db() working to check the
    authorization of a user before and after hitting this endpoint.

    Mocks app.get_user_from_gauth_token() return an idinfo object with
    UPDATER_ID as its 'sub' (user id) field.
    """

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.app.config['COLLECTION'] = mongomock.MongoClient().db.collection
        app.app.config['COLLECTION'].insert_many(FAKE_USERS)  # others
        # insert users that will call the change auth endpoint
        app.app.config['COLLECTION'].insert_one(AUTHORIZED_UPDATER)
        app.app.config['COLLECTION'].insert_one(NON_AUTHORIZED_UPDATER)
        app.app.config['TESTING'] = True  # propagate exceptions to test client
        self.client = app.app.test_client()

    def test_authorized_change_other_true_to_false(self):
        """Authorized user can revoke authorization to other."""
        target_user_id = AUTHORIZED_USER_ID
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))
        self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': False,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_authorized_change_other_false_to_true(self):
        """Authorized user can give authorization to other."""
        target_user_id = NON_AUTHORIZED_USER_ID
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))
        self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': True,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_authorized_change_other_true_to_true(self):
        """Authorized user can trivially keep on authorization of other."""
        target_user_id = AUTHORIZED_USER_ID
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))
        self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': True,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_authorized_change_other_false_to_false(self):
        """Authorized user can trivially keep off authorization of other."""
        target_user_id = NON_AUTHORIZED_USER_ID
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))
        self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': False,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_authorized_change_self_true_to_false(self):
        """Authorized user can revoke authorization of self."""
        target_user_id = AUTHORIZED_UPDATER_ID
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))
        self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': False,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_not_authorized_try_grant_self(self):
        """Not authorized, can't grant authorization to self."""
        # caller not authorized
        app.get_user_from_gauth_token.return_value = IDINFO_NON_AUTHORIZED_UPDATER
        self.assertFalse(app.find_authorization_in_db(
            NON_AUTHORIZED_UPDATER_ID, app.app.config['COLLECTION']))
        # can't give authorization to self
        target_user_id = NON_AUTHORIZED_UPDATER_ID
        result = self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': True,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertIn('Not authorized', result.data.decode())
        self.assertEqual(result.status_code, 403)
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_not_authorized_try_revoke_other(self):
        """Not authorized, can't revoke authorization of other."""
        # caller not authorized
        app.get_user_from_gauth_token.return_value = IDINFO_NON_AUTHORIZED_UPDATER
        self.assertFalse(app.find_authorization_in_db(
            NON_AUTHORIZED_UPDATER_ID, app.app.config['COLLECTION']))
        # can't give authorization to other
        target_user_id = AUTHORIZED_USER_ID
        result = self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': False,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertIn('Not authorized', result.data.decode())
        self.assertEqual(result.status_code, 403)
        self.assertTrue(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_not_authorized_try_grant_other(self):
        """Not authorized, can't grant authorization to other."""
        # caller not authorized
        app.get_user_from_gauth_token.return_value = IDINFO_NON_AUTHORIZED_UPDATER
        self.assertFalse(app.find_authorization_in_db(
            NON_AUTHORIZED_UPDATER_ID, app.app.config['COLLECTION']))
        # can't give authorization to other
        target_user_id = NON_AUTHORIZED_USER_ID
        result = self.client.post('/v1/authorization/update', data={
            'target_user_id': target_user_id,
            'is_organizer': True,
            **DUMMY_GAUTH_REQUEST_DATA})
        self.assertIn('Not authorized', result.data.decode())
        self.assertEqual(result.status_code, 403)
        self.assertFalse(app.find_authorization_in_db(
            target_user_id, app.app.config['COLLECTION']))

    def test_errror_missing_parameters(self):
        """Invalid request missing parameters."""
        result = self.client.post('/v1/authorization/update', data={})
        self.assertIn('Error', result.data.decode())
        self.assertEqual(result.status_code, 400)


if __name__ == '__main__':
    unittest.main()
