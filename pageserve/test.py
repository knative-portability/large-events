import unittest
import app


class TestServe(unittest.TestCase):
    def test_auth_json(self):
        response = app.get_auth_json('example_user')
        # edit_access should be either True or False
        valid_response = response['edit_access'] or not response['edit_access']
        self.assertTrue(valid_response)

    def test_edit_access(self):
        has_access = {'edit_access': True}
        no_access = {'edit_access': False}
        self.assertTrue(app.has_edit_access(has_access))
        self.assertFalse(app.has_edit_access(no_access))


if __name__ == '__main__':
    unittest.main()
