"""Unit tests for users service user upsertion functions."""

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

USER_ID = "valid-user-id"
USER_NAME = "Valid User Name"
ADDITIONAL_INFORMATION = "I'm not found in other documents"


class TestUserUpsertion(unittest.TestCase):
    """Test updating/inserting users into the db."""

    def setUp(self):
        """Seed mock DB for testing."""
        self.mock_collection = mongomock.MongoClient().db.collection

    def test_insert_valid_user(self):
        """A valid user object should be upserted and retrieved correctly.

        Checks the user found after upsertion both against the original
        object added to the database and against the object found with
        the ObjectID returned from app.upsert_user_in_db.
        """
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME,
            "is_organizer": False
        }
        upserted_id = app.upsert_user_in_db(
            user_to_insert, self.mock_collection)
        self.assertIsNotNone(upserted_id)
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        # original user attributes matches found user attributes
        self.assertEqual(user_to_insert["user_id"], found_user["user_id"])
        self.assertEqual(user_to_insert["name"], found_user["name"])
        self.assertEqual(
            user_to_insert["is_organizer"], found_user["is_organizer"])
        # user returned from app.upsert_user_in_db matches found user exactly
        returned_user = self.mock_collection.find_one(upserted_id)
        self.assertEqual(returned_user, found_user)

    def test_malformatted_user_not_inserted(self):
        """A malformatted user_object should not be inserted.

        Note: app.upsert_user_in_db should not insert the user if it is missing
        the 'user_id' or 'name' attributes, but should insert the user if
        the user has more attributes than those. If the user is malformatted,
        app.upsert_user_in_db raises an AttributeError, else it upserts the
        user and returns the new user object.
        """
        # missing name
        with self.assertRaises(AttributeError):
            app.upsert_user_in_db(
                {"user_id": USER_ID, "is_organizer": False},
                self.mock_collection)
        # missing user_id
        with self.assertRaises(AttributeError):
            app.upsert_user_in_db(
                {"name": USER_NAME, "is_organizer": False},
                self.mock_collection)
        # missing is_organizer
        with self.assertRaises(AttributeError):
            app.upsert_user_in_db(
                {"user_id": USER_ID, "name": USER_NAME},
                self.mock_collection)
        # missing all
        with self.assertRaises(AttributeError):
            app.upsert_user_in_db({}, self.mock_collection)
        # too much info
        with self.assertRaises(AttributeError):
            app.upsert_user_in_db(
                {"user_id": USER_ID, "name": USER_NAME, "is_organizer": False,
                 "additional_info": ADDITIONAL_INFORMATION},
                self.mock_collection)
        # no users should have been inserted
        self.assertEqual(self.mock_collection.count_documents({}), 0)

    def test_multiple_upserts_is_one_insert(self):
        """Upserting the same user multiple times should insert once."""
        user_to_insert = {
            "user_id": USER_ID,
            "name": USER_NAME,
            "is_organizer": False
        }
        upserted_id = None
        # upsert many times
        for _ in range(42):
            upserted_id = app.upsert_user_in_db(
                user_to_insert, self.mock_collection)
        # only 1 user has been inserted
        self.assertEqual(self.mock_collection.count_documents({}), 1)
        found_user = self.mock_collection.find_one({"user_id": USER_ID})
        # original user attributes matches found user attributes
        self.assertEqual(user_to_insert["user_id"], found_user["user_id"])
        self.assertEqual(user_to_insert["name"], found_user["name"])
        self.assertEqual(
            user_to_insert["is_organizer"], found_user["is_organizer"])
        # user returned from app.upsert_user_in_db matches found user exactly
        returned_user = self.mock_collection.find_one(upserted_id)
        self.assertEqual(returned_user, found_user)


if __name__ == '__main__':
    unittest.main()
