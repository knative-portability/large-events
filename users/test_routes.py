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


class TestGetAuthorization(unittest.TestCase):
    """Test get authorization endpoint /v1/authorization."""

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


if __name__ == '__main__':
    unittest.main()
