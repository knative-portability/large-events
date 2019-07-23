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
import app
from unittest.mock import patch


class TestServe(unittest.TestCase):
    @patch('app.requests')
    def test_auth_json(self, mock_requests):
        """Checks if users service returns a correctly formatted object.

        A dictionary with a boolean 'edit_access' field should be received.
        """
        mock_response = unittest.mock.MagicMock()
        mock_requests.post.return_value = mock_response
        mock_response.json.return_value = {"edit_access": True}

        response = app.get_user_info('example_user', 'example_url')

        mock_requests.post.assert_called_with(
            'example_url', data={'user_id': 'example_user'})
        valid_response = response['edit_access'] is True
        self.assertTrue(valid_response)

    def test_edit_access(self):
        """Tests if edit access is correctly retrieved from a user dict."""
        has_access = {'edit_access': True}
        no_access = {'edit_access': False}
        self.assertTrue(app.has_edit_access(has_access))
        self.assertFalse(app.has_edit_access(no_access))

    @patch('app.os')
    def test_user_url(self, mock_os):
        """Test retrieval of users URL when defined or not defined."""
        existing_url = "this url exists!"
        mock_os.environ.get.return_value = existing_url
        self.assertEqual(app.get_users_url(), existing_url)

        mock_os.environ.get.return_value = None
        with self.assertRaises(Exception):
            app.get_users_url()


if __name__ == '__main__':
    unittest.main()
