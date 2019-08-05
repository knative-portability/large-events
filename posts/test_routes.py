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
import collections
from bson import ObjectId, json_util
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

DbFile = collections.namedtuple('File', 'filename')
MOCK_DB_FILE = DbFile(filename="the name of a file")

VALID_DB_POST_FULL = {
    "event_id": "foo",
    "author_id": "jrr_tolkien",
    "text": "This is a very valid post with text and files.",
    "files": [
        MOCK_DB_FILE,
        MOCK_DB_FILE
    ]}
VALID_DB_POST_TEXT_NO_FILES = {
    "event_id": "foo",
    "author_id": "ray_bradbury",
    "text": "This post has no files but is still valid.",
    "files": []}
VALID_DB_POST_FILES_NO_TEXT = {
    "event_id": "bar",
    "author_id": "No text is alright if I have files.",
    "text": "",
    "files": [
        MOCK_DB_FILE
    ]}


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


class TestGetAllPostsRoute(unittest.TestCase):
    """Test get all posts endpoint GET /v1/."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()

    def assert_count_in_collection(self, query, target_count):
        """Assert the count of a given object in the database."""
        self.assertEqual(
            app.config["COLLECTION"].count_documents(query), target_count)

    def test_no_posts_found(self):
        """Get all posts but no posts are in the db."""
        num_expected_posts = 0
        self.assert_count_in_collection({}, num_expected_posts)
        result = self.client.get("/v1/")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)

    def test_multiple_posts_found(self):
        """Get all posts and multiple posts in the db."""
        mock_posts = [
            VALID_DB_POST_FULL,
            VALID_DB_POST_TEXT_NO_FILES,
            VALID_DB_POST_FILES_NO_TEXT]
        num_expected_posts = len(mock_posts)
        app.config["COLLECTION"].insert_many(mock_posts)
        self.assert_count_in_collection({}, num_expected_posts)
        result = self.client.get("/v1/")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)


class TestGetPostByPostIDRoute(unittest.TestCase):
    """Test get post by post ID endpoint GET /v1/<post_id>."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        self.mock_posts = [
            VALID_DB_POST_FULL,
            VALID_DB_POST_TEXT_NO_FILES,
            VALID_DB_POST_FILES_NO_TEXT]
        app.config["COLLECTION"].insert_many(self.mock_posts)
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()

    def test_no_post_found(self):
        """Can't find post with given ID in the db."""
        num_expected_posts = 0
        id_not_in_db = "C001""1C3D""C0FFEE""D0000000DE"
        result = self.client.get(f"/v1/{id_not_in_db}")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)

    def test_yes_post_found(self):
        """Find a post by ID."""
        num_expected_posts = 1
        post_id = self.mock_posts[0]["_id"]
        result = self.client.get(f"/v1/{str(post_id)}")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)
        self.assertEqual(data["posts"][0]["_id"], post_id)


class TestGetPostByEventIDRoute(unittest.TestCase):
    """Test get post by event  endpoint GET /v1/by_event/<event_id>."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        self.mock_posts = [
            VALID_DB_POST_FULL,
            VALID_DB_POST_TEXT_NO_FILES,
            VALID_DB_POST_FILES_NO_TEXT]
        app.config["COLLECTION"].insert_many(self.mock_posts)
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()

    def test_no_post_found(self):
        """Can't find post with given event ID in the db."""
        num_expected_posts = 0
        id_not_in_db = "C001""1C3D""C0FFEE""D0000000DE"
        result = self.client.get(f"/v1/by_event/{id_not_in_db}")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)

    def test_yes_post_found(self):
        """Find multiple posts by event ID."""
        event_id = self.mock_posts[0]["event_id"]
        expected_posts = [
            post for post in self.mock_posts if post["event_id"] is event_id]
        num_expected_posts = len(expected_posts)
        result = self.client.get(f"/v1/by_event/{str(event_id)}")
        self.assertEqual(result.status_code, 200)
        data = json_util.loads(result.data)
        self.assertEqual(data["num_posts"], num_expected_posts)
        self.assertEqual(len(data["posts"]), num_expected_posts)
        self.assertEqual(data["posts"], expected_posts)


class TestDeletePostByPostIDRoute(unittest.TestCase):
    """Test delete post by post ID endpoint DELETE /v1/<post_id>."""

    def setUp(self):
        """Set up test client and seed mock DB for testing."""
        app.config["COLLECTION"] = mongomock.MongoClient().db.collection
        self.mock_posts = [
            VALID_DB_POST_FULL,
            VALID_DB_POST_TEXT_NO_FILES,
            VALID_DB_POST_FILES_NO_TEXT]
        app.config["COLLECTION"].insert_many(self.mock_posts)
        app.config["TESTING"] = True  # propagate exceptions to test client
        self.client = app.test_client()

    def test_delete_one(self):
        """Delete a single post."""
        post_id = self.mock_posts[0]["_id"]
        author_id = self.mock_posts[0]["author_id"]
        result = self.client.delete(
            f"/v1/{str(post_id)}/delete", data={"author_id": author_id})
        self.assertEqual(result.status_code, 204)
        self.assertEqual(app.config["COLLECTION"].count_documents({}),
                         len(self.mock_posts) - 1)

    def test_delete_all(self):
        """Delete all posts."""
        for post in self.mock_posts:
            post_id = post["_id"]
            author_id = post["author_id"]
            result = self.client.delete(
                f"/v1/{str(post_id)}/delete", data={"author_id": author_id})
            self.assertEqual(result.status_code, 204)
        self.assertEqual(app.config["COLLECTION"].count_documents({}), 0)

    def test_not_existing_post_id(self):
        """Can't find post by ID, don't delete."""
        post_id = "C001""1C3D""C0FFEE""D0000000DE"   # invalid
        author_id = self.mock_posts[0]["author_id"]  # valid
        result = self.client.delete(
            f"/v1/{str(post_id)}/delete", data={"author_id": author_id})
        self.assertEqual(result.status_code, 404)
        self.assertEqual(app.config["COLLECTION"].count_documents({}),
                         len(self.mock_posts))

    def test_not_existing_author_id(self):
        """Wrong author_id, don't delete."""
        post_id = self.mock_posts[0]["_id"]              # valid
        author_id = "I don't think, therefore I'm not."  # invalid
        result = self.client.delete(
            f"/v1/{str(post_id)}/delete", data={"author_id": author_id})
        self.assertEqual(result.status_code, 404)
        self.assertEqual(app.config["COLLECTION"].count_documents({}),
                         len(self.mock_posts))

    def test_mismatched_author_id(self):
        """Wrong author_id, don't delete."""
        post_id = self.mock_posts[0]["_id"]          # valid
        author_id = self.mock_posts[1]["author_id"]  # valid, but doesn't match
        result = self.client.delete(
            f"/v1/{str(post_id)}/delete", data={"author_id": author_id})
        self.assertEqual(result.status_code, 404)
        self.assertEqual(app.config["COLLECTION"].count_documents({}),
                         len(self.mock_posts))

    def test_no_author_id(self):
        """No author_id, don't delete."""
        post_id = self.mock_posts[0]["_id"]          # valid
        result = self.client.delete(
            f"/v1/{str(post_id)}/delete")
        self.assertEqual(result.status_code, 400)
        self.assertEqual(app.config["COLLECTION"].count_documents({}),
                         len(self.mock_posts))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
