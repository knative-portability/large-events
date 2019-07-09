import unittest
from app import *

class TestServe(unittest.TestCase):
    def test_get_auth(self):
        self.assertTrue(get_auth("carolyn"))
        self.assertFalse(get_auth("Voldemort"))
        
        
if __name__ == '__main__':
    unittest.main()
