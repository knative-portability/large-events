import unittest
import datetime
import app


EXAMPLE_TIME = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)
EXAMPLE_TIME_STRING = EXAMPLE_TIME.isoformat(" ", "seconds")


class TestEventsClass(unittest.TestCase):
    def setUp(self):
        self.test_info = {'name': 'test_event',
                          'description': 'testing!',
                          'author': 'admin',
                          'event_time': EXAMPLE_TIME,
                          'created_at': EXAMPLE_TIME}
        self.test_info_with_id = dict(event_id=1, **self.test_info)
        self.test_info_with_db_id = dict(event_id=1, _id=2, **self.test_info)

    def test_construct_event(self):
        event = app.Event(**self.test_info)
        self.test_info['event_id'] = None
        self.assertEqual(event.dict, self.test_info)

        event_with_id = app.Event(**self.test_info_with_id)
        self.assertEqual(event_with_id.dict, self.test_info_with_id)

        event_with_db_id = app.Event(**self.test_info_with_db_id)
        self.test_info_with_db_id['event_id'] = 2
        del self.test_info_with_db_id['_id']
        self.assertEqual(event_with_db_id.dict, self.test_info_with_db_id)

    def test_constuct_event_error(self):
        info_missing_name = self.test_info.copy()
        del info_missing_name['name']
        info_extra_field = self.test_info.copy()
        info_extra_field['extra'] = 'hello'

        with self.assertRaises(ValueError):
            app.Event(**info_missing_name)
        with self.assertRaises(ValueError):
            app.Event(**info_extra_field)

    def test_events_equal(self):
        event = app.Event(**self.test_info)
        event_same = app.Event(**self.test_info)
        event_with_id = app.Event(**self.test_info_with_id)
        self.assertEqual(event, event_same)
        self.assertEqual(event, event_with_id)

    def test_events_unequal(self):
        test_info_diff = self.test_info.copy()
        test_info_diff['name'] = 'different event'

        event = app.Event(**self.test_info)
        event_diff = app.Event(**test_info_diff)
        self.assertNotEqual(event, event_diff)

    def test_events_equal_time_rounding(self):
        test_info_time = self.test_info.copy()
        test_info_time['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100000)
        test_info_unrounded = self.test_info.copy()
        test_info_unrounded['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100435)

        event_rounded = app.Event(**test_info_time)
        event_unrounded = app.Event(**test_info_unrounded)
        self.assertEqual(event_rounded, event_unrounded)

    def test_events_unequal_time(self):
        test_info_time = self.test_info.copy()
        test_info_time['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100000)
        test_info_diff = self.test_info.copy()
        test_info_diff['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 0)

        event = app.Event(**test_info_time)
        event_diff = app.Event(**test_info_diff)
        self.assertNotEqual(event, event_diff)

    def test_events_time_string(self):
        test_info_str_time = self.test_info.copy()
        test_info_str_time['created_at'] = EXAMPLE_TIME_STRING
        self.test_info['created_at'] = EXAMPLE_TIME_STRING
        self.assertEqual(self.test_info, test_info_str_time)

        self.test_info['created_at'] = EXAMPLE_TIME_STRING + " different str"
        self.assertNotEqual(self.test_info, test_info_str_time)


if __name__ == '__main__':
    unittest.main()
