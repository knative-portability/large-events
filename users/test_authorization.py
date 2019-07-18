"""Unit tests for users service authorization functions."""

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
import mongomock
import app

AUTHORIZED_USER = "authorized-user"
NON_AUTHORIZED_USER = "non-authorized-user"
MALFORMATTED_IN_DB_USER = "this-user-has-no-'is_organizer'_db_field"
MISSING_USER = "not-a-user-in-the-database"


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service."""

    def setUp(self):
        """Seed mock DB for testing"""
        self.mock_collection = mongomock.MongoClient().db.collection
        mock_data = [
            {"user_id": AUTHORIZED_USER,
             "name": AUTHORIZED_USER,
             "is_organizer": True},
            {"user_id": NON_AUTHORIZED_USER,
             "name": NON_AUTHORIZED_USER,
             "is_organizer": False},
            {"user_id": MALFORMATTED_IN_DB_USER}
        ]
        self.mock_collection.insert_many(mock_data)

    def test_authorized_user_is_authorized(self):
        """An authorized user should receive authorized privileges."""
        self.assertTrue(app.find_authorization_in_db(
            AUTHORIZED_USER, self.mock_collection))

    def test_non_authorized_user_not_authorized(self):
        """A non-authorized user should not receive authorized privileges."""
        self.assertFalse(app.find_authorization_in_db(
            NON_AUTHORIZED_USER, self.mock_collection))

    def test_malformatted_user_none_authorization(self):
        """An incorrect db schema should not receive authorized privileges."""
        self.assertFalse(app.find_authorization_in_db(
            MALFORMATTED_IN_DB_USER, self.mock_collection))

    def test_unkown_user_not_authorized(self):
        """A user not in the db should not receive authorized privileges."""
        self.assertFalse(app.find_authorization_in_db(
            MISSING_USER, self.mock_collection))


if __name__ == '__main__':
    unittest.main()
