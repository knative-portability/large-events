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
import app


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service"""

    def setUp(self):
        """Seed DB for testing"""
        self.id_of_test_user_is_organizer = "test-is-organizer-12345"
        self.id_of_test_user_not_organizer = "test-not-organizer-12345"
        # update or insert (upsert) a new user
        app.DB.users.update_one(
            {"username": self.id_of_test_user_is_organizer},
            {"$set": {"username": self.id_of_test_user_is_organizer,
                      "name": self.id_of_test_user_is_organizer,
                      "is_organizer": True}},
            upsert=True)
        app.DB.users.update_one(
            {"username": self.id_of_test_user_not_organizer},
            {"$set": {"username": self.id_of_test_user_not_organizer,
                      "name": self.id_of_test_user_not_organizer,
                      "is_organizer": False}},
            upsert=True)

    def test_good_user_is_authorized(self):
        """An authorized user should have authorized privileges"""
        self.assertTrue(app.is_authorized_to_edit(
            self.id_of_test_user_is_organizer))

    def test_bad_user_not_authorized(self):
        """An non-authorized user should not have authorized privileges"""
        self.assertFalse(app.is_authorized_to_edit(
            self.id_of_test_user_not_organizer))

    def test_unkown_user_not_authorized(self):
        """An user not found in the db should not have authorized privileges"""
        self.assertFalse(app.is_authorized_to_edit(
            "notAValidUsername31415926"))

    def tearDown(self):
        """Clean up test users"""
        app.DB.users.delete_many(
            {"$or": [
                {"username": self.id_of_test_user_is_organizer},
                {"username": self.id_of_test_user_not_organizer}]})


if __name__ == '__main__':
    unittest.main()
