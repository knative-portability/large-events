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
import pymongo
from flask import Flask, jsonify, request

app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/v1/add', methods=['POST'])
def upload_new_post():
    """Make a new post upload to the server.

    Post request body should contain:
    event_id: id of the event to post to
    author_id: user id of the user making the post
    text: text to be sent
    Post request files should contain all the files the user wants to upload
    to the server.
    """


@app.route('/v1/', methods=['GET'])
def get_all_posts():
    """Get all posts for the whole event."""


@app.route('/v1/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    """Get the post with the specified ID."""


@app.route('/v1/by_event/<event_id>', methods=['GET'])
def get_all_posts_for_event(event_id):
    """Get all posts matching the event with the specified ID."""


def connect_to_mongodb():  # pragma: no cover
    """Connect to MongoDB instance using env vars."""

    class DBNotConnectedError(EnvironmentError):
        """Raised when not able to connect to the db."""

    class Thrower(object):
        """Used to raise an exception on failed db connect."""

        def __getattribute__(self, _):
            raise DBNotConnectedError(
                "Not able to find MONGODB_URI environmental variable")

    mongodb_uri = os.environ.get("MONGODB_URI")
    if mongodb_uri is None:
        return Thrower()  # not able to find db config var
    return pymongo.MongoClient(mongodb_uri).users_db


DB = connect_to_mongodb()  # None if can't connect

if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
