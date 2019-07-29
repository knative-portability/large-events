"""Copyright 2019 The Knative Authors

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
from unittest import mock
import app


class TestServe(unittest.TestCase):
    """Test helper functions in pageserve app."""

    def setUp(self):
        """Create secret key for test session."""
        app.app.secret_key = "Secret test key!"

    def test_get_user(self):
        """Checks if users service returns a correctly formatted object.

        Expects a user dictionary with a boolean 'is_organizer' field.
        This test mocks app.authenticate_with_users_service() to always
        return the response of an authenticated user that is authorized.
        """
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"is_organizer": True}
        with mock.patch("app.authenticate_with_users_service",
                        return_value=mock_response):
            app.session = {"user": {
                "user_id": "abc123 pretend I am a user ID.",
                "name": "Boaty McBoatface",
                "gauth_token": "Pretend I am a valid GAuth token."}}
            result = app.get_user()

            valid_response = result["is_organizer"] is True
            self.assertTrue(valid_response)

            # now test no user in session
            app.session.clear()
            result = app.get_user()
            self.assertIsNone(result)

    def test_edit_access(self):
        """Tests if authorization is correctly retrieved from a user dict.

        This test mocks away requests to the users service which is normally
        called by app.has_edit_access.
        """
        # is authorized
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"edit_access": True}
        with mock.patch("app.requests.post", return_value=mock_response):
            self.assertTrue(app.has_edit_access(
                {"user_id": "Pretend I am authorized."}))
        # not authorized
        mock_response.json.return_value = {"edit_access": False}
        with mock.patch("app.requests.post", return_value=mock_response):
            self.assertFalse(app.has_edit_access(
                {"user_id": "Pretend I am NOT authorized."}))
        # No user sent give no authorization. This might happens when a user
        # is logged out so app.get_user() returns None.
        self.assertFalse(app.has_edit_access(None))

    @mock.patch('app.os')
    def test_config_endpoints(self, mock_os):
        """Test retrieval of endpoint env vars when defined or not defined."""
        existing_endpoint = 'this endpoint exists!'
        example_endpoints = ['url1', 'url2']
        mock_os.environ.__contains__.return_value = True
        mock_os.environ.get.return_value = existing_endpoint
        app.config_endpoints(example_endpoints)
        self.assertEqual(app.app.config['url1'], existing_endpoint)
        self.assertEqual(app.app.config['url2'], existing_endpoint)

        mock_os.environ.__contains__.return_value = False
        with self.assertRaises(NameError):
            app.config_endpoints(['url3'])


if __name__ == '__main__':
    unittest.main()
