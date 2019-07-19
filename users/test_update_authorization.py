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


class TestUpdateAuthorization(unittest.TestCase):
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

    def test_change_authorization(self):
        """Can change the authorization to the opposite value."""
        # True to False
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])
        app.update_user_authorization_in_db(
            AUTHORIZED_USER, False, self.mock_collection)
        self.assertFalse(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])
        # False to True
        self.assertFalse(self.mock_collection.find_one(
            {"user_id": NON_AUTHORIZED_USER})["is_organizer"])
        app.update_user_authorization_in_db(
            NON_AUTHORIZED_USER, True, self.mock_collection)
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": NON_AUTHORIZED_USER})["is_organizer"])

    def test_keep_authorization_the_same(self):
        """Can trivially change the authorization to the same value."""
        # True to True
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])
        app.update_user_authorization_in_db(
            AUTHORIZED_USER, True, self.mock_collection)
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])
        # False to False
        self.assertFalse(self.mock_collection.find_one(
            {"user_id": NON_AUTHORIZED_USER})["is_organizer"])
        app.update_user_authorization_in_db(
            NON_AUTHORIZED_USER, False, self.mock_collection)
        self.assertFalse(self.mock_collection.find_one(
            {"user_id": NON_AUTHORIZED_USER})["is_organizer"])

    def test_set_authorization_of_malformed_user(self):
        """Can set the authorization of a user missing the attribute in db."""
        self.assertNotIn("is_organizer", self.mock_collection.find_one(
            {"user_id": MALFORMATTED_IN_DB_USER}))
        app.update_user_authorization_in_db(
            MALFORMATTED_IN_DB_USER, False, self.mock_collection)
        self.assertFalse(self.mock_collection.find_one(
            {"user_id": MALFORMATTED_IN_DB_USER})["is_organizer"])

    def test_fail_on_missing_user(self):
        """Should raise error and do nothing on user missing from db."""
        self.assertIsNone(self.mock_collection.find_one(
            {"user_id": MISSING_USER}))
        with self.assertRaises(KeyError):
            app.update_user_authorization_in_db(
                MISSING_USER, False, self.mock_collection)
        # make sure no user was inserted
        self.assertIsNone(self.mock_collection.find_one(
            {"user_id": MISSING_USER}))

    def test_fail_on_bad_arg_type(self):
        """Should raise error and do nothing on bad arg type."""
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])
        with self.assertRaises(TypeError):
            app.update_user_authorization_in_db(
                AUTHORIZED_USER, "False", self.mock_collection)
        # type/value not changed
        self.assertTrue(self.mock_collection.find_one(
            {"user_id": AUTHORIZED_USER})["is_organizer"])


if __name__ == '__main__':
    unittest.main()
