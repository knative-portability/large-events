"""Main flask app for posts.
    - Serve stored media
    - Upload new posts to database
"""

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

import os
import uuid
import json
import datetime
import pymongo
from bson import json_util, ObjectId
from flask import Flask, request
from werkzeug.exceptions import BadRequestKeyError
from google.cloud import storage

app = Flask(__name__)  # pylint: disable=invalid-name

REQUIRED_ATTRIBUTES = {'event_id', 'author_id', 'text', 'files'}


@app.route('/v1/', methods=['GET'])
def get_all_posts():
    """Get all posts for the whole event."""
    # serialize otherwise nonserializable ObjectIDs
    post_list = find_posts_in_db(app.config['COLLECTION'])
    return serialize_posts_to_json(post_list)


@app.route('/v1/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    """Get the post with the specified ID.
    """
    post_list = find_posts_in_db(
        app.config['COLLECTION'], post_id=ObjectId(post_id))
    return serialize_posts_to_json(post_list)


@app.route('/v1/<post_id>', methods=['DELETE'])
def delete_post_by_id(post_id):
    """Delete the post with the specified ID.

    On deletion, only deletes posts matching post_id and with an author_id
    matching the request parameter's author ID. Assumes that the passed in
    author_id is authenticated and non-malicious. I.e. this should only be
    deployed as an internal service accessible by only the other microservices.
    """
    try:
        author_id = request.form['author_id']
        return delete_post(post_id, author_id, app.config['COLLECTION'])
    except BadRequestKeyError:
        return 'Error: request missing `author_id`.', 400


@app.route('/v1/add', methods=['POST'])
def upload_new_post():
    """Make a new post upload to the server.

    Post request body should contain multipart/form-data with:
    event_id: id of the event to post to
    author_id: user id of the user making the post
    text: text to be sent
    All the files the user wants to upload
    to the server.
    """
    try:
        post = {
            'event_id': request.form['event_id'],
            'author_id': request.form['author_id'],
            'text':  request.form['text'],
            'files': [file for file in request.files.values()]
        }
        return str(upload_new_post_to_db(post, app.config['COLLECTION'])), 201
    except BadRequestKeyError:
        return f'Invalid request. Required data: {REQUIRED_ATTRIBUTES}.', 400
    except ValueError:
        return 'Post must contain text and/or files.', 400


@app.route('/v1/by_event/<event_id>', methods=['GET'])
def get_all_posts_for_event(event_id):
    """Get all posts matching the event with the specified ID."""
    # serialize otherwise nonserializable ObjectIDs
    post_list = find_posts_in_db(app.config['COLLECTION'], event_id=event_id)
    return serialize_posts_to_json(post_list)


def delete_post(post_id, author_id, collection):
    """Deletes the post matching post_id and author_id if it exists."""
    result = collection.delete_one(
        {'_id': ObjectId(post_id), 'author_id': author_id})
    return (('Document deleted.', 204) if result.deleted_count
            else ('Document not found.', 404))


def find_posts_in_db(collection, post_id=None, event_id=None):
    """Finds all matching posts in the database.

    Query is configured using one or none of args `post_id` and `event_id`.
    If one is not None, searches for matching posts.
    If both are not None, post_id takes precedence.
    If both are None, then searches for all posts.

    Args:
        collection (pymongo.collection): The collection to search in.
        post_id (string): ID of a post to search for.
        event_id (string): ID of an event to find all posts for.

    Returns:
        list: List of all matching post objects.
    """
    query = {}
    if post_id is not None:
        query = {'_id': post_id}
    elif event_id is not None:
        query = {'event_id': event_id}
    cursor = collection.find(query)
    list_of_posts = []
    for post in cursor:
        list_of_posts.append(post)
    return list_of_posts


def generate_timestamp():
    """Generate timestamp of the current time for placement in db.

    Returns:
        datetime: the current time.
    """
    return datetime.datetime.utcnow().isoformat(sep=' ', timespec='seconds')


def serialize_posts_to_json(post_list):
    """Serialize the post list into a json object.

    Used for sending the results of a post query in an HTTP response.
    Handles non-serializable fields like bson.ObjectID.

    Args:
        post_list (list): List of post objects to serialize

    Returns:
        dict: json-like wrapper around the list of posts in a 'posts' key
            and the number of posts in a 'num_posts' key.
    """
    return json.loads(json_util.dumps(
        {'posts': post_list,
         'num_posts': len(post_list)}))


def upload_file_to_cloud(file):
    """Uploads a file to the GCloud Storage bucket.

    Returns:
        str: Public URL of the file in the cloud.
    """
    filename = str(uuid.uuid4()) + '-' + file.filename
    blob = CLOUD_STORAGE_BUCKET.blob(filename)
    blob.upload_from_file(file)
    return blob.public_url


def upload_new_post_to_db(post, collection):
    """Uploads a new post to the db collection.

    Assumes the event matching the post's `event_id` and the user matching
        the post's `author_id` both exist. I.e. Caller should check this.

    Args:
        post (dict): Post to add. Requires exactly the following attributes:
            event_id (str): id of the event to post to
            author_id (str): user id of the user making the post
            text (str): text description
            files (list): list of strings of file URLs
        collection: pymongo collection to insert into.

    Returns:
        ObjectID: DB ID of the post that was uploaded.

    Raises:
        ValueError: Has no text body (i.e. empty string) nor any files
            to upload.
        AttributeError: `post` has not enough or too many attributes.
    """
    if post.keys() != REQUIRED_ATTRIBUTES:
        raise AttributeError(f'Post must have exactly the '
                             'attributes {required_attributes}')
    if not post['text'] and not post['files']:
        raise ValueError('One of text or files must not be empty.')
    # post is valid, add on timestamp, upload files, insert into db
    post['created_at'] = generate_timestamp()
    post['files'] = [
        upload_file_to_cloud(file) for file in post['files']]
    return collection.insert_one(post).inserted_id


def connect_to_cloud_storage():  # pragma: no cover
    """Connect to Google Cloud Storage using env vars."""

    class StorageNotConnectedError(ConnectionError):
        """Raised when not able to connect to the storage."""

    class Thrower():  # pylint: disable=too-few-public-methods
        """Used to raise an exception on failed storage connect."""

        def __getattribute__(self, _):
            raise StorageNotConnectedError(
                'Not able to find GCLOUD_STORAGE_BUCKET_NAME environment variable')

    bucket_name = os.environ.get('GCLOUD_STORAGE_BUCKET_NAME')
    if bucket_name is None:
        return Thrower()  # not able to find storage config var
    storage_client = storage.Client()
    return storage_client.get_bucket(bucket_name)


CLOUD_STORAGE_BUCKET = connect_to_cloud_storage()


def connect_to_mongodb():  # pragma: no cover
    """Connect to MongoDB instance using env vars."""

    class DBNotConnectedError(ConnectionError):
        """Raised when not able to connect to the db."""

    class Thrower():  # pylint: disable=too-few-public-methods
        """Used to raise an exception on failed db connect."""

        def __getattribute__(self, _):
            raise DBNotConnectedError(
                'Not able to find MONGODB_URI environment variable')

    mongodb_uri = os.environ.get('MONGODB_URI')
    if mongodb_uri is None:
        return Thrower()  # not able to find db config var
    return pymongo.MongoClient(mongodb_uri).posts_db.posts_collection


app.config['COLLECTION'] = connect_to_mongodb()


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
