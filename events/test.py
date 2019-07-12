import unittest
import datetime
import app


class TestEventsDB(unittest.TestCase):
    def setUp(self):
        # TODO(cmei4444): move this to a mock DB to avoid the official DB
        # interfering with tests
        self.example_time = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)
        self.event_info = {'name': 'test_event',
                           'description': 'testing!',
                           'author': 'admin',
                           'event_time': '7-12-2019',
                           'created_at': self.example_time}
        self.test_event = app.Event(self.event_info)
        # make sure DB has no other test entries
        app.events_coll.delete_many(self.event_info)

    def test_add(self):
        self.test_event.add_to_db()
        queried_event = app.events_coll.find_one(self.event_info)
        self.assertEqual(app.Event(queried_event), self.test_event)

    def test_build_info(self):
        test_info = {'name': 'test_event',
                     'description': 'testing!',
                     'author': 'admin',
                     'event_time': '7-12-2019', }
        time = datetime.datetime(2017, 8, 28, 10, 33, 1, 100000)
        info = app.build_event_info(test_info, time)
        self.assertEqual(info['created_at'], time)

        time_unrounded = datetime.datetime(2017, 8, 28, 10, 33, 1, 100654)
        info = app.build_event_info(test_info, time_unrounded)
        self.assertEqual(info['created_at'], time)

    def tearDown(self):
        app.events_coll.delete_many(
            self.event_info)    # empty DB of test entries


class TestEventsClass(unittest.TestCase):
    def setUp(self):
        self.test_info = {'name': 'test_event',
                          'description': 'testing!',
                          'author': 'admin',
                          'event_time': '7-12-2019',
                          'created_at': '7-10-2019'}
        self.test_info_with_id = {'name': 'test_event',
                                  'description': 'testing!',
                                  'author': 'admin',
                                  'event_time': '7-12-2019',
                                  'created_at': '7-10-2019',
                                  'event_id': 1}

    def test_construct_event(self):
        event = app.Event(self.test_info)
        self.test_info['event_id'] = None
        self.assertEqual(event.info, self.test_info)

        event_with_id = app.Event(self.test_info_with_id)
        self.assertEqual(event_with_id.info, self.test_info_with_id)

    def test_events_equal(self):
        test_info_diff = self.test_info.copy()
        test_info_diff['name'] = 'different event'

        event = app.Event(self.test_info)
        event_same = app.Event(self.test_info)
        event_with_id = app.Event(self.test_info_with_id)
        self.assertEqual(event, event_same)
        self.assertEqual(event, event_with_id)

        event_diff = app.Event(test_info_diff)
        self.assertNotEqual(event, event_diff)

    def test_is_valid(self):
        valid_event = app.Event(self.test_info)
        self.assertTrue(valid_event.is_valid())

        del self.test_info['name']
        invalid_event = app.Event(self.test_info)
        self.assertFalse(invalid_event.is_valid())


if __name__ == '__main__':
    unittest.main()
