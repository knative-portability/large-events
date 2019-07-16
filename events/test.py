import unittest
import datetime
import app
import mongomock


example_time = datetime.datetime(2019, 6, 11, 10, 33, 1, 100000)


class TestEventsDB(unittest.TestCase):
    def setUp(self):
        self.event_info = {'name': 'test_event',
                           'description': 'testing!',
                           'author': 'admin',
                           'event_time': example_time,
                           'created_at': example_time}
        self.test_event = app.Event(self.event_info)
        # Create mock DB for testing
        self.client = mongomock.MongoClient()
        self.test_coll = self.client.eventsDB.all_events

    def test_add(self):
        self.test_event.add_to_db(self.test_coll)
        queried_event = self.test_coll.find_one(self.event_info)
        self.assertEqual(app.Event(queried_event), self.test_event)

    def test_build_info(self):
        test_info = {'name': 'test_event',
                     'description': 'testing!',
                     'author': 'admin',
                     'event_time': example_time, }
        info = app.build_event_info(test_info, example_time)
        self.assertEqual(info['created_at'], example_time)

    def tearDown(self):
        self.client.drop_database("eventsDB")


class TestEventsClass(unittest.TestCase):
    def setUp(self):
        self.test_info = {'name': 'test_event',
                          'description': 'testing!',
                          'author': 'admin',
                          'event_time': example_time,
                          'created_at': example_time}
        self.test_info_with_id = dict(event_id=1, **self.test_info)
        self.test_info_with_db_id = dict(event_id=1, _id=2, **self.test_info)

    def test_construct_event(self):
        event = app.Event(self.test_info)
        self.test_info['event_id'] = None
        self.assertEqual(event.dict, self.test_info)

        event_with_id = app.Event(self.test_info_with_id)
        self.assertEqual(event_with_id.dict, self.test_info_with_id)

        event_with_db_id = app.Event(self.test_info_with_db_id)
        self.assertEqual(event_with_db_id.dict, self.test_info_with_db_id)

    def test_constuct_event_error(self):
        info_missing_name = self.test_info.copy()
        del info_missing_name['name']
        info_extra_field = self.test_info.copy()
        info_extra_field['extra'] = 'hello'

        self.assertRaises(ValueError, app.Event, info_missing_name)
        self.assertRaises(ValueError, app.Event, info_extra_field)

    def test_events_equal(self):
        event = app.Event(self.test_info)
        event_same = app.Event(self.test_info)
        event_with_id = app.Event(self.test_info_with_id)
        self.assertEqual(event, event_same)
        self.assertEqual(event, event_with_id)

    def test_events_unequal(self):
        test_info_diff = self.test_info.copy()
        test_info_diff['name'] = 'different event'

        event = app.Event(self.test_info)
        event_diff = app.Event(test_info_diff)
        self.assertNotEqual(event, event_diff)

    def test_events_equal_time_rounding(self):
        test_info_time = self.test_info.copy()
        test_info_time['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100000)
        test_info_unrounded = self.test_info.copy()
        test_info_unrounded['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100435)

        event_rounded = app.Event(test_info_time)
        event_unrounded = app.Event(test_info_unrounded)
        self.assertEqual(event_rounded, event_unrounded)

    def test_events_unequal_time(self):
        test_info_time = self.test_info.copy()
        test_info_time['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 100000)
        test_info_diff = self.test_info.copy()
        test_info_diff['created_at'] = datetime.datetime(
            2017, 8, 28, 10, 33, 1, 0)

        event = app.Event(test_info_time)
        event_diff = app.Event(test_info_diff)
        event_time_as_str = app
        self.assertNotEqual(event, event_diff)

        test_info_diff_timestr = self.test_info.copy()
        test_info_diff_timestr['created_at'] = "different time"

        event_timestr = app.Event(self.test_info)
        event_timestr_diff = app.Event(test_info_diff_timestr)
        self.assertNotEqual(event_timestr, event_timestr_diff)


if __name__ == '__main__':
    unittest.main()
