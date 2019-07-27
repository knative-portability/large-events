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
from unittest.mock import patch
import app


class TestServe(unittest.TestCase):
    @patch('app.requests')
    def test_get_user(self, mock_requests):
        """Checks if users service returns a correctly formatted object.

        Expects a user dictionary with a boolean 'is_organizer' field.
        """
        mock_response = unittest.mock.MagicMock()
        mock_requests.post.return_value = mock_response
        mock_response.json.return_value = {"is_organizer": True}

        # TODO(mukobi) fix this test
        pass
        # with app.app.test_client() as client:
        #     with client.session_transaction() as session:
        #         session["user"] = {
        #             "user_id": "I don't matter, requests is mocked."}
        #         response = app.get_user()

        #         mock_requests.post.assert_called_once()
        #         valid_response = response["is_organizer"] is True
        #         self.assertTrue(valid_response)

    def test_edit_access(self):
        """Tests if authorization is correctly retrieved from a user dict."""
        has_access = {'is_organizer': True}
        no_access = {'is_organizer': False}
        self.assertTrue(app.has_edit_access(has_access))
        self.assertFalse(app.has_edit_access(no_access))

    @patch('app.os')
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
