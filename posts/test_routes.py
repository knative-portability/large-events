"""Unit tests for posts service HTTP routes."""

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
import io
from bson import ObjectId
import mongomock
from app import app

MOCK_FILE_URL = "the url of an uploaded file"

VALID_REQUEST_FULL = {
    "event_id": "abc123",
    "author_id": "jrr_tolkien",
    "text": "This is a very valid post with text and files.",
    "file_1": (io.BytesIO(b'first file contents'), "file_1.jpg"),
    "file_2": (io.BytesIO(b'other file contents'), "file_2.jpg")}
VALID_REQUEST_TEXT_NO_FILES = {
    "event_id": "abc123",
    "author_id": "ray_bradbury",
    "text": "This post has no files but is still valid."}
VALID_REQUEST_FILES_NO_TEXT = {
    "event_id": "abc123",
    "author_id": "No text is alright if I have files.",
    "text": "",
    "file_1": (io.BytesIO(b'first file contents'), "file_1.jpg")}
INVALID_REQUEST_NO_TEXT_NOR_FILES = {
    "event_id": "abc123",
    "author_id": "I'm missing text and files and am invalid.",
    "text": ""}
INVALID_REQUEST_NOT_ENOUGH_ATTRS = {
    "where_did_all_the_attributes_go?": "I don't know"}


class TestUploadNewPostRoute(unittest.TestCase):
    """Test upload new post endpoint POST /v1/add."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()
        # mock Google Cloud Storage bucket for file uploading
        patcher = mock.patch("app.CLOUD_STORAGE_BUCKET")
        self.mock_bucket = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_bucket.blob().public_url = MOCK_FILE_URL

    def assert_count_in_collection(self, query, target_count):
        """Assert the count of a given object in the database."""
        self.assertEqual(
            app.config["COLLECTION"].count_documents(query), target_count)

    def test_upload_full_post(self):
        """Valid upload of post with text and files."""
        result = self.client.post("/v1/add", data=VALID_REQUEST_FULL,
                                  content_type="multipart/form-data")
        self.assertEqual(result.status_code, 201)
        self.assert_count_in_collection(
            {"_id": ObjectId(result.data.decode())}, 1)

    def test_upload_text_no_files(self):
        """Valid upload of post with text but no files."""
        result = self.client.post("/v1/add", data=VALID_REQUEST_TEXT_NO_FILES,
                                  content_type="multipart/form-data")
        self.assertEqual(result.status_code, 201)
        self.assert_count_in_collection(
            {"_id": ObjectId(result.data.decode())}, 1)

    def test_upload_files_no_text(self):
        """Valid upload of post with files but no text."""
        result = self.client.post("/v1/add", data=VALID_REQUEST_FILES_NO_TEXT,
                                  content_type="multipart/form-data")
        self.assertEqual(result.status_code, 201)
        self.assert_count_in_collection(
            {"_id": ObjectId(result.data.decode())}, 1)

    def test_invalid_no_text_nor_files(self):
        """Invalid upload of post with no text nor files."""
        result = self.client.post("/v1/add",
                                  data=INVALID_REQUEST_NO_TEXT_NOR_FILES,
                                  content_type="multipart/form-data")
        self.assertEqual(result.status_code, 400)
        self.assert_count_in_collection({}, 0)

    def test_invalid_not_enough_attrs(self):
        """Invalid upload of post with not enough attributes."""
        result = self.client.post("/v1/add",
                                  data=INVALID_REQUEST_NOT_ENOUGH_ATTRS,
                                  content_type="multipart/form-data")
        self.assertEqual(result.status_code, 400)
        self.assert_count_in_collection({}, 0)


if __name__ == '__main__':
    unittest.main()
