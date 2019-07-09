import unittest
import app


class TestServe(unittest.TestCase):
    def test_get_auth(self):
        self.assertTrue(app.get_auth("carolyn"))
        self.assertFalse(app.get_auth("Voldemort"))


if __name__ == '__main__':
    unittest.main()
