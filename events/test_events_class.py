import unittest
import datetime
import app


EXAMPLE_TIME_STRING = datetime.datetime(
    2019, 6, 11, 10, 33, 1, 100000).isoformat(sep=" ", timespec="seconds")


class TestEventsClass(unittest.TestCase):
    def setUp(self):
        self.test_info = {'name': 'test_event',
                          'description': 'testing!',
                          'author': 'admin',
                          'event_time': EXAMPLE_TIME_STRING,
                          'created_at': EXAMPLE_TIME_STRING}
        self.test_info_with_id = dict(event_id=1, **self.test_info)
        self.test_info_with_db_id = dict(event_id=1, _id=2, **self.test_info)

    def test_construct_event(self):
        event = app.Event(**self.test_info)
        result_dict = dict(event_id=None, **self.test_info)
        self.assertEqual(event.dict, result_dict)

        event_with_id = app.Event(**self.test_info_with_id)
        result_dict = dict(_id=1, **self.test_info)
        self.assertEqual(event_with_id.dict, result_dict)

        event_with_db_id = app.Event(**self.test_info_with_db_id)
        result_dict = dict(_id=2, **self.test_info)
        self.assertEqual(event_with_db_id.dict, result_dict)

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

    def test_events_equal_times(self):
        test_info_str_time = self.test_info.copy()
        test_info_str_time['created_at'] = EXAMPLE_TIME_STRING
        self.test_info['created_at'] = EXAMPLE_TIME_STRING
        self.assertEqual(self.test_info, test_info_str_time)

    def test_events_unequal_times(self):
        test_info_str_time = self.test_info.copy()
        test_info_str_time['created_at'] = EXAMPLE_TIME_STRING
        self.test_info['created_at'] = EXAMPLE_TIME_STRING + " different str"
        self.assertNotEqual(self.test_info, test_info_str_time)


if __name__ == '__main__':
    unittest.main()
