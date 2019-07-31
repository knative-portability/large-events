"""Unit tests for posts uploading."""

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
from unittest import mock
import datetime
import collections
import mongomock
import app

MOCK_FILE_URL = "the url of an uploaded file"
File = collections.namedtuple('File', 'filename')
MOCK_FILE = File(filename="the name of a file")

VALID_POST_FULL = {
    "event_id": "abc123",
    "author_id": "jrr_tolkien",
    "text": "This is a very valid post with text and files.",
    "files": [
        MOCK_FILE,
        MOCK_FILE
    ]}
VALID_POST_TEXT_NO_FILES = {
    "event_id": "abc123",
    "author_id": "ray_bradbury",
    "text": "This post has no files but is still valid.",
    "files": []}
VALID_POST_FILES_NO_TEXT = {
    "event_id": "abc123",
    "author_id": "No text is alright if I have files.",
    "text": "",
    "files": [
        MOCK_FILE
    ]}
INVALID_POST_NO_TEXT_NOR_FILES = {
    "event_id": "abc123",
    "author_id": "I'm missing text and files and am invalid.",
    "text": "",
    "files": []}
INVALID_POST_NOT_ENOUGH_ATTRS = {
    "where_did_all_the_attributes_go?": "I don't know"}
INVALD_POST_TOO_MANY_ATTRS = {
    "event_id": "abc123",
    "author_id": "grr_martin",
    "text": "I have a valid description but too many fields.",
    "files": [],
    "woah_where_did_I_come_from?": "malicious data"}


class TestPostUploading(unittest.TestCase):
    """Test post uploading of users service."""

    def assert_posts_are_equal(self, first, second):
        """Asserts that the 2 posts have equal data.

        Only looks at required post attributes
        (event_id, author_id, text, files).
        """
        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(first["author_id"], second["author_id"])
        self.assertEqual(first["text"], second["text"])
        self.assertEqual(first["files"], second["files"])

    def setUp(self):
        """Set up mocks for testing."""
        # mock db
        self.mock_collection = mongomock.MongoClient().db.collection
        # mock Google Cloud Storage bucket for file uploading
        patcher = mock.patch("app.CLOUD_STORAGE_BUCKET")
        self.mock_bucket = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_bucket.blob().public_url = MOCK_FILE_URL

    def test_full_upload(self):
        """Can upload a full post object with both text and files."""
        app.upload_new_post_to_db(VALID_POST_FULL, self.mock_collection)
        self.mock_bucket.blob().upload_from_file.assert_called()
        post_in_db = self.mock_collection.find_one({})
        self.assertIsNotNone(post_in_db)
        self.assert_posts_are_equal(VALID_POST_FULL, post_in_db)

    def test_partial_upload_no_files(self):
        """Can upload a post with text but no files."""
        app.upload_new_post_to_db(
            VALID_POST_TEXT_NO_FILES, self.mock_collection)
        # no files to upload to bucket
        self.mock_bucket.blob().upload_from_file.assert_not_called()
        post_in_db = self.mock_collection.find_one({})
        self.assertIsNotNone(post_in_db)
        self.assert_posts_are_equal(VALID_POST_TEXT_NO_FILES, post_in_db)

    def test_partial_upload_no_text(self):
        """Can upload a post with files but no text."""
        app.upload_new_post_to_db(
            VALID_POST_FILES_NO_TEXT, self.mock_collection)
        self.mock_bucket.blob().upload_from_file.assert_called()
        post_in_db = self.mock_collection.find_one({})
        self.assertIsNotNone(post_in_db)
        self.assert_posts_are_equal(VALID_POST_FILES_NO_TEXT, post_in_db)

    def test_empty_upload(self):
        """Cannot upload a post without text and files."""
        with self.assertRaises(ValueError):
            app.upload_new_post_to_db(
                INVALID_POST_NO_TEXT_NOR_FILES, self.mock_collection)
        # no posts were uploaded
        self.assertIsNone(self.mock_collection.find_one({}))

    def test_not_enough_attrs_upload(self):
        """Cannot upload a post missing required post attributes."""
        with self.assertRaises(AttributeError):
            app.upload_new_post_to_db(
                INVALID_POST_NOT_ENOUGH_ATTRS, self.mock_collection)
        # no posts were uploaded
        self.assertIsNone(self.mock_collection.find_one({}))

    def test_too_many_attrs_upload(self):
        """Cannot upload a post with too many attributes."""
        with self.assertRaises(AttributeError):
            app.upload_new_post_to_db(
                INVALD_POST_TOO_MANY_ATTRS, self.mock_collection)
        # no posts were uploaded
        self.assertIsNone(self.mock_collection.find_one({}))


class TestGenerateTimestamp(unittest.TestCase):
    """Test app.generate_timestamp()."""

    def test_happy_case(self):
        """Happy case of normal timestamp generation."""
        test_time = datetime.datetime(1999, 12, 15, 3, 23, 3, 318274)
        mock_datetime = mock.MagicMock()
        mock_datetime.datetime.now.return_value = test_time
        with mock.patch("app.datetime", mock_datetime):
            self.assertEqual(app.generate_timestamp(), test_time)


if __name__ == '__main__':
    unittest.main()
