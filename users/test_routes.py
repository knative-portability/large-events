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
from app import app

AUTHORIZED_USER = "authorized-user"
NON_AUTHORIZED_USER = "non-authorized-user"
MALFORMATTED_IN_DB_USER = "this-user-has-no-'is_organizer'_db_field"
MISSING_USER = "not-a-user-in-the-database"

FAKE_USERS = [
    {"user_id": AUTHORIZED_USER,
     "name": AUTHORIZED_USER,
     "is_organizer": True},
    {"user_id": NON_AUTHORIZED_USER,
     "name": NON_AUTHORIZED_USER,
     "is_organizer": False},
    {"user_id": MALFORMATTED_IN_DB_USER}
]

IDINFO_VALID = {
    "iss": "accounts.google.com",
    "sub": "A Google user ID",
    "name": "John Doe"}
IDINFO_INVALID_ISSUER = {
    "iss": "malicious.site.net"}
DUMMY_GAUTH_REQUEST_DATA = {"gauth_token": "fake_token_0123"}


class TestGetAuthorization(unittest.TestCase):
    """Test get authorization endpoint POST /v1/authorization."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["COLLECTION"].insert_many(FAKE_USERS)
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()

    def test_is_authorized(self):
        """Get authorization of authorized user."""
        result = self.client.post(
            "/v1/authorization", data={"user_id": AUTHORIZED_USER})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {"edit_access": True})

    def test_not_authorized(self):
        """Get authorization of non-authorized user."""
        result = self.client.post(
            "/v1/authorization", data={"user_id": NON_AUTHORIZED_USER})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {"edit_access": False})

    def test_malformatted_in_db(self):
        """Get authorization of user that is malformatted in the db."""
        result = self.client.post(
            "/v1/authorization", data={"user_id": MALFORMATTED_IN_DB_USER})
        self.assertEqual(result.status_code, 200)
        response_body = json.loads(result.data)
        self.assertEqual(response_body, {"edit_access": False})

    def test_missing_param(self):
        """Try to get authorization but don't supply user_id."""
        result = self.client.post("/v1/authorization")
        self.assertEqual(result.status_code, 400)


class TestAuthenticateUser(unittest.TestCase):
    """Test authenticate user endpoint POST /v1/authenticate."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()
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
            "/v1/authenticate", data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = json.loads(result.data)
        self.assert_equal_idinfos(response_body, IDINFO_VALID)
        self.assertEqual(result.status_code, 201)

    def test_no_authentication_token(self):
        """No token provided."""
        result = self.client.post(
            "/v1/authenticate")
        response_body = result.data.decode()
        self.assertIn("Error", response_body)
        self.assertEqual(result.status_code, 400)

    def test_bad_issuer(self):
        """Bad token issuer (not Google Accounts)."""
        self.verify_oauth2_token.return_value = IDINFO_INVALID_ISSUER
        result = self.client.post(
            "/v1/authenticate", data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = result.data.decode()
        self.assertIn("Error", response_body)
        self.assertEqual(result.status_code, 400)

    def test_authentication_failed(self):
        """Authentication failed due to invalid token.

        This might occur when the token has expired, it's Google OAuth
        client ID does not match that of the server, or the token is
        otherwise invalid.
        """
        self.verify_oauth2_token.side_effect = ValueError("Bad token.")
        result = self.client.post(
            "/v1/authenticate", data=DUMMY_GAUTH_REQUEST_DATA)
        response_body = result.data.decode()
        self.assertIn("Error", response_body)
        self.assertEqual(result.status_code, 400)


if __name__ == '__main__':
    unittest.main()
