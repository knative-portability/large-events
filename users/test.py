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
from app import is_authorized_to_edit


class TestAuthorization(unittest.TestCase):
    """Test /authorization endpoint of users service"""

    def test_good_user_is_authorized(self):
        """An authorized user should have authorized privileges"""
        self.assertTrue(is_authorized_to_edit("carolyn", None))

    def test_bad_user_not_authorized(self):
        """An non-authorized user should not have authorized privileges"""
        self.assertFalse(is_authorized_to_edit("Voldemort", None))


if __name__ == '__main__':
    unittest.main()
