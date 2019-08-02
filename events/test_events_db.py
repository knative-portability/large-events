"""Unit tests for events database access."""

# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def test_build_events_dict(self):
        """Checks response dict is built correctly from queried events."""
        for _ in range(10):
            self.test_coll.insert_one(self.test_event.dict)
        events = self.test_coll.find()
        events_dict = app.build_events_dict(events)
        for i in range(10):
            self.assertIsInstance(events_dict['events'][i], dict)
            retrieved_event = app.Event(**events_dict['events'][i])
            self.assertEqual(retrieved_event, self.test_event)
        self.assertEqual(events_dict['num_events'], 10)

    def test_build_info(self):
        test_info = {'name': 'test_event',
                     'description': 'testing!',
                     'author': 'admin',
                     'event_time': EXAMPLE_TIME, }
        info = app.build_event_info(test_info, EXAMPLE_TIME)
        self.assertEqual(info['created_at'], EXAMPLE_TIME)


if __name__ == '__main__':
    unittest.main()
