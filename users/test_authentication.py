"""Unit tests for users service authentication functions."""

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
from unittest import mock
import app

IDINFO_VALID = {
    "iss": "accounts.google.com"}
IDINFO_INVALID_ISSUER = {
    "iss": "malicious.site.net"}


class TestGetUserFromGAuthToken(unittest.TestCase):
    """Test app.get_user_from_gauth_token().

    Uses the google-auth package to decode a gauth_token, so instead
    of suppplying real tokens, we mock the functionality of
    google.oauth2.id_token to simulate different responses from
    different tokens.
    """

    def setUp(self):
        """Patch google.oauth2.id_token."""
        patcher = mock.patch('app.id_token')
        self.verify_oauth2_token = patcher.start().verify_oauth2_token
        self.addCleanup(patcher.stop)

    def test_valid_token(self):
        """Simulate extracting a valid token."""
        self.verify_oauth2_token.return_value = IDINFO_VALID
        result = app.get_user_from_gauth_token(None)
        self.assertEqual(result, IDINFO_VALID)

    def test_bad_issuer(self):
        """Bad token issuer (not Google Accounts)."""
        self.verify_oauth2_token.return_value = IDINFO_INVALID_ISSUER
        with self.assertRaises(ValueError):
            app.get_user_from_gauth_token(None)

    def test_authentication_failed(self):
        """Authentication failed due to invalid token.

        This might occur when the token has expired, it's Google OAuth
        client ID does not match that of the server, or the token is
        otherwise invalid.
        """
        self.verify_oauth2_token.side_effect = ValueError("Bad token.")
        with self.assertRaises(ValueError):
            app.get_user_from_gauth_token(None)


if __name__ == '__main__':
    unittest.main()
