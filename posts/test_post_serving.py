"""Unit tests for posts serving."""

# Authors: mukobi
# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import mongomock
import app

FAKE_POSTS = [
    {
        "post_id": "abc123",
        "event_id": "picnic",
        "author_id": "mukobi",
        "created_at": "2017-10-06T00:00:00+00:00",
        "text": "This is the description of a picnic post.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/6/66/"
            "An_up-close_picture_of_a_curious_male_domestic_short"
            "hair_tabby_cat.jpg",
            "http://4.bp.blogspot.com/-w8U75TCuhgU/Tzw8TmaclvI/AA"
            "AAAAAABJ0/6fMMcRLAceM/s1600/Rabbit3.jpg"
        ]
    },
    {
        "post_id": "def456",
        "event_id": "aquarium",
        "author_id": "mukobi",
        "created_at": "2011-11-11T00:00:00+00:00",
        "text": "This is the description of an aquarium post.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/0/02/"
            "Sea_Otter_%28Enhydra_lutris%29_%2825169790524%29_crop.jpg"
        ]
    },
    {
        "post_id": "ghi789",
        "event_id": "aquarium",
        "author_id": "john_wick",
        "created_at": "2014-10-24T00:00:00+00:00",
        "text": "This is another aquarium post.",
        "images": []
    }
]


class TestPostDBGetting(unittest.TestCase):
    """Test app.find_posts_in_db()."""

    def setUp(self):
        """Seed mock db."""
        self.collection = mongomock.MongoClient().db.collection
        self.collection.insert_many(FAKE_POSTS)

    def test_find_all_posts(self):
        """Find all fake posts."""
        found = app.find_posts_in_db(self.collection)
        self.assertEqual(found, FAKE_POSTS)

    def test_find_by_post_id(self):
        """Search for 1 post by post ID."""
        post_id = FAKE_POSTS[0]["post_id"]
        found = app.find_posts_in_db(self.collection, post_id=post_id)
        expected = [post for post in FAKE_POSTS if post["post_id"] is post_id]
        self.assertEqual(found, expected)

    def test_find_by_event_id(self):
        """Search for many posts by event ID."""
        event_id = "aquarium"
        found = app.find_posts_in_db(self.collection, event_id=event_id)
        expected = [post for post in FAKE_POSTS if post["event_id"] is event_id]
        self.assertEqual(found, expected)

    def test_missing_all_posts(self):
        """Can't find any posts in an empty db."""
        self.collection.delete_many({})  # empty the db
        found = app.find_posts_in_db(self.collection)
        expected = []
        self.assertEqual(found, expected)

    def test_missing_post_id(self):
        """Can't find any posts for a given post ID."""
        post_id = "This ID doesn't match any post 09876544321"
        found = app.find_posts_in_db(self.collection, post_id=post_id)
        expected = []
        self.assertEqual(found, expected)

    def test_missing_event_id(self):
        """Can't find any posts for a given event ID."""
        event_id = "This ID doesn't match any event 09876544321"
        found = app.find_posts_in_db(self.collection, event_id=event_id)
        expected = []
        self.assertEqual(found, expected)


if __name__ == '__main__':
    unittest.main()
