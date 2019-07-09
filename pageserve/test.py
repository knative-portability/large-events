import unittest
from app import *

# currently not working
class TestServe(unittest.TestCase):
    def test1(self):
        self.assertTrue(get_auth("carolyn"))
        self.assertFalse(get_auth("Voldemort"))
        
    def test2(self):
        pass
        
        
if __name__ == '__main__':
    unittest.main()
