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
import ast
import requests_mock
import flask
from app import app

VALID_USER_IN_SESSION = {
    "user_id": "42",
    "name": "Ford Prefect"}
ERROR_BAD_TOKEN_TEXT = "Error: bad gauth_token."
ERROR_BAD_TOKEN_STATUS = 400
VALID_USER_AUTH_STATUS = 201


class TestAuthenticateAndGetUser(unittest.TestCase):
    """Test authentication endpoint POST /v1/authenticate."""

    def assert_sessions_are_equal(self, first, second):
        """Asserts the two sessions are the same.

        Only compares the "user_id" and "name" fields, but ignores the
        "gauth_token" field which is not returned from the users service
        but is stored in the session by app.authenticate_with_users_service.
        """
        self.assertEqual(first["user_id"], second["user_id"])
        self.assertEqual(first["name"], second["name"])

    def setUp(self):
        """Set up test client."""
        app.config["TESTING"] = True  # propagate exceptions to test client
        app.secret_key = "Dummy key used for testing the flask session"

    @requests_mock.Mocker()
    def test_valid_authentication(self, requests_mocker):
        """GAuth token successfully authenticates."""
        with app.test_request_context(), app.test_client() as client:
            requests_mocker.post(app.config["USERS_ENDPOINT"] + "authenticate",
                                 json=VALID_USER_IN_SESSION,
                                 status_code=VALID_USER_AUTH_STATUS)
            result = client.post("/v1/authenticate", data={
                "gauth_token": "I don't matter because requests is mocked"})
            self.assertEqual(result.status_code, VALID_USER_AUTH_STATUS)
            result_dict = ast.literal_eval(result.data.decode())
            self.assert_sessions_are_equal(
                result_dict, VALID_USER_IN_SESSION)
            # user stored in session
            self.assertEqual(len(flask.session), 1)
            self.assert_sessions_are_equal(
                flask.session["user"], VALID_USER_IN_SESSION)

    @requests_mock.Mocker()
    def test_failed_authentication(self, requests_mocker):
        """GAuth token fails authentication."""
        with app.test_request_context(), app.test_client() as client:
            requests_mocker.post(app.config["USERS_ENDPOINT"] + "authenticate",
                                 text=ERROR_BAD_TOKEN_TEXT,
                                 status_code=ERROR_BAD_TOKEN_STATUS)
            result = client.post("/v1/authenticate", data={
                "gauth_token": "I don't matter because requests is mocked"})
            self.assertEqual(result.status_code, ERROR_BAD_TOKEN_STATUS)
            self.assertEqual(result.data.decode(), ERROR_BAD_TOKEN_TEXT)
            # user not stored in session
            self.assertEqual(len(flask.session), 0)
            self.assertNotIn("user", flask.session)

    def test_no_token_given(self):
        """Failed to provide a GAuth token to authenticate."""
        with app.test_request_context(), app.test_client() as client:
            result = client.post("/v1/authenticate")
            self.assertEqual(result.status_code, 400)
            self.assertIn("Error", result.data.decode())
            # nothing stored in session
            self.assertEqual(len(flask.session), 0)


class TestSignOut(unittest.TestCase):
    """Test sign out endpoint GET /v1/sign_out."""

    def setUp(self):
        """Set up test client."""
        app.config["TESTING"] = True  # propagate exceptions to test client
        app.secret_key = "Dummy key used for testing the flask session"

    def test_was_logged_in(self):
        """Sign out a user that was logged in (usual behaviour)."""
        with app.test_request_context(), app.test_client() as client:
            flask.session["user"] = VALID_USER_IN_SESSION
            # user in session before
            self.assertIn("user", flask.session)
            self.assertEqual(len(flask.session), 1)
            result = client.get(
                "/v1/sign_out")
            # empty session after
            self.assertNotIn("user", flask.session)
            self.assertEqual(len(flask.session), 0)
            # correct redirect response
            self.assertEqual(result.status_code, 302)  # redirect
            self.assertIn("redirect", result.data.decode())

    def test_was_not_logged_in(self):
        """Try to sign out a user that was not logged in."""
        with app.test_request_context(), app.test_client() as client:
                # empty session before
            self.assertNotIn("user", flask.session)
            self.assertEqual(len(flask.session), 0)
            result = client.get(
                "/v1/sign_out")
            # empty session after
            self.assertNotIn("user", flask.session)
            self.assertEqual(len(flask.session), 0)
            # correct redirect response
            self.assertEqual(result.status_code, 302)  # redirect
            self.assertIn("redirect", result.data.decode())


if __name__ == '__main__':
    unittest.main()
