"""Main flask app for users service

Features include
    - adding/updating users in the users db
    - getting the authorization level of a user
"""

# Author: mukobi
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
from flask import Flask, jsonify, request
import pymongo
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)  # pylint: disable=invalid-name

app.config["GAUTH_CLIENT_ID"] = os.environ.get("GAUTH_CLIENT_ID")


@app.route('/v1/authorization', methods=['POST'])
def get_authorization():
    """Finds whether the given user is authorized for edit access."""
    user = request.form.get('user_id')
    if user is None:
        return "Error: You must supply a 'user_id' POST parameter!", 400
    authorized = find_authorization_in_db(user, app.config["COLLECTION"])
    return jsonify(edit_access=authorized)


@app.route('/v1/authenticate', methods=['PUT'])
def authenticate_user():
    """Authenticate user, upsert in the db, and return new user object.

    Request data:
        'gauth_token': Google ID token to authenticate.

    Response:
        201: user object as it is in the db if authentication
            was successful.
        400: error message if authentication was not successful.
    """
    gauth_token = request.form.get('gauth_token')
    if gauth_token is None:
        return "Error: You must supply a valid gauth_token.", 400
    try:
        idinfo = get_user_from_gauth_token(gauth_token)
        user_object = {
            "user_id": idinfo["sub"],
            "name": idinfo["name"],
            "is_organizer": False}  # authorization defaults false
        upsert_user_in_db(user_object, app.config["COLLECTION"])
        return user_object, 201
    except (AttributeError, ValueError) as error:
        return f"Error: {error}", 400


def get_user_from_gauth_token(gauth_token):
    """Validate the Google auth token and return it's user object.

    Args:
        gauth_token (str): Google ID token to authenticate.

    Returns:
        dict: User object. Contains attributes including:
            'sub': Unique user ID.
            'name': Full name of user.
            'email': Email of user.
            ...

    Raises:
        ValueError: Token is invalid.
    """
    # Authenticate token and match to client ID
    idinfo = id_token.verify_oauth2_token(
        gauth_token, requests.Request(), app.config["GAUTH_CLIENT_ID"])

    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong authentication token issuer.')

    # ID token is valid. Return the user object.
    return idinfo


def upsert_user_in_db(user_object, users_collection):
    """Updates or inserts the user object into users_collection.

    Args:
        user_object (dict): must contain a user_id, name, and is_organizer,
            and must not contain other attributes.
        users_collection (pymongo.collection): the MongoDB collection to use.

    Returns:
        ObjectID: The ID of the upserted object from the db. This can be used
            to find the object with collection.find_one(object_id).

    Raises:
        AttributeError: if user_object is malformatted.
    """
    required_attributes = {"user_id", "name", "is_organizer"}
    if user_object.keys() != required_attributes:
        raise AttributeError("malformatted user object")
    # upsert user in db
    return users_collection.update_one(
        {"user_id": user_object["user_id"]},
        {"$set": user_object},
        upsert=True).upserted_id


def update_user_authorization_in_db(
        user_id: str, is_organizer: bool, users_collection):
    """Updates the authorization of the given user in the database.

    Args:
        user_id (str): The id of the user to change.
        is_organizer (bool): The authorization value to set.

    Returns:
        ObjectID: The ID of the updated object from the db. This can be used
            to find the object with `collection.find_one(object_id)`.

    Raises:
        KeyError: Bad `user_id`/user not found in db.
        TypeError: `is_organizer` is not a bool.
    """
    if not isinstance(is_organizer, bool):
        raise TypeError("Trying to set authorization to a non-bool type.")
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"is_organizer": bool(is_organizer)}},
        upsert=False)
    if result.matched_count == 0:
        raise KeyError(f"User with ID '{user_id}' not found.'")
    return result.upserted_id


def find_authorization_in_db(username, users_collection):
    """Queries the db to find authorization of the given user."""
    first_user = users_collection.find_one({"user_id": username})
    if first_user is None:  # user not found
        return False
    authorized = first_user.get("is_organizer")
    return bool(authorized)  # handle 'None' case


def connect_to_mongodb():  # pragma: no cover
    """Connect to MongoDB instance using env vars."""

    class DBNotConnectedError(ConnectionError):
        """Raised when not able to connect to the db."""

    class Thrower():  # pylint: disable=too-few-public-methods
        """Used to raise an exception on failed db connect."""

        def __getattribute__(self, _):
            raise DBNotConnectedError(
                "Not able to find MONGODB_URI environment variable")

    mongodb_uri = os.environ.get("MONGODB_URI")
    if mongodb_uri is None:
        return Thrower()  # not able to find db config var
    return pymongo.MongoClient(mongodb_uri).users_db.users_collection


app.config["COLLECTION"] = connect_to_mongodb()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
