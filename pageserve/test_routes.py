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
from unittest import mock
import flask
from app import app

VALID_USER_SESSION = {
    "user_id": "42",
    "name": "Ford Prefect"
}


class TestSignOut(unittest.TestCase):
    """Test sign out endpoint GET /v1/sign_out."""

    def setUp(self):
        """Set up test client."""
        app.config["TESTING"] = True  # propagate exceptions to test client
        app.secret_key = "Dummy key used for testing the flask session"
        self.client = app.test_client()

    def test_was_logged_in(self):
        """Sign out a user that was logged in (usual behaviour)."""
        with app.test_request_context():
            with mock.patch.dict("app.session", VALID_USER_SESSION, clear=True):
                result = self.client.get(
                    "/v1/sign_out")
                # popped session
                self.assertNotIn("user", flask.session)
                # correct response
                self.assertEqual(result.status_code, 302)  # redirect
                self.assertIn("redirect", result.data.decode())

    def test_was_not_logged_in(self):
        """Try to sign out a user that was not logged in."""
        with app.test_request_context():
            # empty session before
            self.assertNotIn("user", flask.session)
            result = self.client.get(
                "/v1/sign_out")
            # empty session after
            self.assertNotIn("user", flask.session)
            # correct response
            self.assertEqual(result.status_code, 302)  # redirect
            self.assertIn("redirect", result.data.decode())


if __name__ == '__main__':
    unittest.main()
