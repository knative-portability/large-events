"""
users/test.py
Authors: mukobi
Unit tests for users service


Copyright 2019 The Knative Authors

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
import mongomock
from app import find_authorization_in_db, upsert_user_in_db

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
        self.assertTrue(find_authorization_in_db(
            AUTHORIZED_USER, self.mock_collection))

    def test_non_authorized_user_not_authorized(self):
        """A non-authorized user should not receive authorized privileges."""
        self.assertFalse(find_authorization_in_db(
            NON_AUTHORIZED_USER, self.mock_collection))

    def test_malformatted_user_none_authorization(self):
        """An incorrect db schema should not receive authorized privileges."""
        self.assertFalse(find_authorization_in_db(
            MISSING_USER, self.mock_collection))

    def test_unkown_user_not_authorized(self):
        """A user not in the db should not receive authorized privileges."""
        self.assertFalse(find_authorization_in_db(
            MALFORMATTED_IN_DB_USER, self.mock_collection))


class TestUserUpsertion(unittest.TestCase):
    """Test updating/inserting users into the db."""
    USER_ID = "valid-user-id"
    USER_NAME = "Valid User Name"
    ADDITIONAL_INFORMATION = "I'm not found in other documents"

    def test_insert_valid_user(self):
        """A valid user object should be upserted and retrieved correctly."""
        self.mock_collection = mongomock.MongoClient().db.collection
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME
        }
        self.assertTrue(upsert_user_in_db(
            user_to_insert, self.mock_collection))
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        self.assertEqual(user_to_insert["user_id"], found_user["user_id"])
        self.assertEqual(user_to_insert["name"], found_user["name"])

    def test_user_auth_default_false(self):
        """The 'is_organizer' field of an inserted user should be False."""
        self.mock_collection = mongomock.MongoClient().db.collection
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME
        }
        self.assertTrue(upsert_user_in_db(
            user_to_insert, self.mock_collection))
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        self.assertFalse(found_user["is_organizer"])

    def test_malformatted_user_not_inserted(self):
        """A malformatted user_object should not be inserted.

        Note: upsert_user_in_db should not insert the user if it is missing
        the 'user_id' or 'name' attributes, but should insert the user if
        the user has more attributes than those. If the user is malformatted,
        upsert_user_in_db returns False, else it upserts the user and returns
        True.
        """
        self.mock_collection = mongomock.MongoClient().db.collection
        # missing name
        self.assertFalse(upsert_user_in_db(
            {"user_id": USER_ID}, self.mock_collection))
        # missing user_id
        self.assertFalse(upsert_user_in_db(
            {"name": USER_NAME}, self.mock_collection))
        # missing both
        self.assertFalse(upsert_user_in_db(
            {}, self.mock_collection))
        # no users should have been inserted
        self.assertEqual(self.mock_collection.count_documents({}), 0)

    def test_additional_info_still_inserted(self):
        """A user_object with additional information should still be inserted.

        Note: upsert_user_in_db should not insert the user if it is missing
        the 'user_id' or 'name' attributes, but should insert the user if
        the user has more attributes than those. If the user is malformatted,
        upsert_user_in_db returns False, else it upserts the user and returns
        True.
        """
        self.mock_collection = mongomock.MongoClient().db.collection
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME,
            "additional_info": ADDITIONAL_INFORMATION
        }
        self.assertTrue(upsert_user_in_db(
            user_to_insert, self.mock_collection))
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        self.assertEqual(user_to_insert["user_id"], found_user["user_id"])
        self.assertEqual(user_to_insert["name"], found_user["name"])
        self.assertEqual(user_to_insert["additional_info"],
                         found_user["additional_info"])

    def test_multiple_upserts_is_one_insert(self):
        """Upserting the same user multiple times should insert once."""
        self.mock_collection = mongomock.MongoClient().db.collection
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME
        }
        # upsert many times
        for i in range(0, 42):
            self.assertTrue(upsert_user_in_db(
                user_to_insert, self.mock_collection))
        # only 1 user has been inserted
        self.assertEqual(self.mock_collection.count_documents({}), 1)
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        self.assertEqual(user_to_insert["user_id"], found_user["user_id"])
        self.assertEqual(user_to_insert["name"], found_user["name"])


if __name__ == '__main__':
    unittest.main()
