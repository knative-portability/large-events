"""
users/test.py
Authors: mukobi
Unit tests for users service
"""

import unittest
from app import is_authorized

class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service"""
    def test_good_user_is_authorized(self):
        """An authorized user should have authorized privileges"""
        self.assertTrue(is_authorized("carolyn", None))

    def test_bad_user_not_authorized(self):
        """An non-authorized user should not have authorized privileges"""
        self.assertFalse(is_authorized("Voldemort", None))


if __name__ == '__main__':
    unittest.main()
