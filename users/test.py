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
from app import is_authorized_to_edit


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service."""

    def setUp(self):
        """Seed mock DB for testing"""
        self.id_of_test_user_is_authorized = "authorized-user"
        self.id_of_test_user_not_authorized = "non-authorized-user"
        self.id_of_test_user_not_in_db = "not-a-user-in-the-database"
        self.mock_collection = mongomock.MongoClient().db.collection
        mock_data = [
            {"username": self.id_of_test_user_is_authorized,
             "name": self.id_of_test_user_is_authorized,
             "is_organizer": True},
            {"username": self.id_of_test_user_not_authorized,
             "name": self.id_of_test_user_not_authorized,
             "is_organizer": False}
        ]
        self.mock_collection.insert_many(mock_data)

    def test_authorized_user_is_authorized(self):
        """An authorized user should receive authorized privileges."""
        self.assertTrue(is_authorized_to_edit(
            self.id_of_test_user_is_authorized, self.mock_collection))

    def test_non_authorized_user_not_authorized(self):
        """An non-authorized user should not receive authorized privileges."""
        self.assertFalse(is_authorized_to_edit(
            self.id_of_test_user_not_authorized, self.mock_collection))

    def test_unkown_user_not_authorized(self):
        """An user not in the db should not receive authorized privileges."""
        self.assertFalse(is_authorized_to_edit(
            self.id_of_test_user_not_in_db, self.mock_collection))


if __name__ == '__main__':
    unittest.main()
