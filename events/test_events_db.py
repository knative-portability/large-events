import unittest
import datetime
import mongomock
import app


EXAMPLE_TIME = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)


class TestEventsDB(unittest.TestCase):
    def setUp(self):
        self.event_info = {'name': 'test_event',
                           'description': 'testing!',
                           'author': 'admin',
                           'event_time': EXAMPLE_TIME,
                           'created_at': EXAMPLE_TIME}
        self.test_event = app.Event(**self.event_info)
        # Create mock DB for testing
        self.client = mongomock.MongoClient()
        self.test_coll = self.client.eventsDB.all_events

    def test_add(self):
        app.add_to_db(self.test_event.dict, self.test_coll)
        queried_event = self.test_coll.find_one(self.event_info)
        self.assertEqual(app.Event(**queried_event), self.test_event)

    def test_build_info(self):
        test_info = {'name': 'test_event',
                     'description': 'testing!',
                     'author': 'admin',
                     'event_time': EXAMPLE_TIME, }
        info = app.build_event_info(test_info, EXAMPLE_TIME)
        self.assertEqual(info['created_at'], EXAMPLE_TIME)


if __name__ == '__main__':
    unittest.main()
