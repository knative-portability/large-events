"""
users/test.py
Authors: mukobi
Unit tests for users service
"""

import unittest
import app


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service"""

    def setUp(self):
        """Seed DB for testing"""
        # update or insert (upsert) a new user
        app.DB.users.update(
            {"username": "mukobi"},
            {"username": "mukobi",
             "name": "Gabriel Mukobi",
             "is_organizer": True},
            upsert=True)
        app.DB.users.update(
            {"username": "foobar"},
            {"username": "foobar",
             "name": "Unauthorized User",
             "is_organizer": False},
            upsert=True)

    def test_good_user_is_authorized(self):
        """An authorized user should have authorized privileges"""
        self.assertTrue(app.is_authorized_to_edit("mukobi"))

    def test_bad_user_not_authorized(self):
        """An non-authorized user should not have authorized privileges"""
        self.assertFalse(app.is_authorized_to_edit("foobar"))

    def test_unkown_user_not_authorized(self):
        """An user not found in the db should not have authorized privileges"""
        self.assertFalse(app.is_authorized_to_edit(
            "notAValidUsername31415926"))


if __name__ == '__main__':
    unittest.main()
