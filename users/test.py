"""
users/test.py
Authors: mukobi
Unit tests for users service
"""

import unittest
import app


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service"""

    def test_good_user_is_authorized(self):
        """An authorized user should have authorized privileges"""
        self.assertTrue(app.is_authorized_to_edit("mukobi"))

    def test_bad_user_not_authorized(self):
        """An non-authorized user should not have authorized privileges"""
        self.assertFalse(app.is_authorized_to_edit("foobar"))


if __name__ == '__main__':
    unittest.main()
