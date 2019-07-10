"""
users/app.py
Authors: mukobi
Main flask app for users service
    - adding/updating users in the users db
    - getting the authorization level of a user
"""

import os
from pprint import pprint  # for printing MongoDB data
from flask import Flask, jsonify, request
import pymongo

app = Flask(__name__)  # pylint: disable=invalid-name

# connect to MongoDB Atlas database
MONGODB_ATLAS_USERNAME = os.environ.get(
    "MONGODB_ATLAS_USERNAME")
MONGODB_ATLAS_PASSWORD = os.environ.get(
    "MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_CLUSTER_ADDRESS = os.environ.get(
    "MONGODB_ATLAS_CLUSTER_ADDRESS")
DB = pymongo.MongoClient(
    "mongodb+srv://{}:{}@{}".format(
        MONGODB_ATLAS_USERNAME,
        MONGODB_ATLAS_PASSWORD,
        MONGODB_ATLAS_CLUSTER_ADDRESS)).test

# update or insert (upsert) a new user
DB.users.update(
    {"username": "cmei4444"},
    {"username": "cmei4444",
     "name": "Carolyn Mei",
     "is_organizer": True},
    upsert=True)
DB.users.update(
    {"username": "mukobi"},
    {"username": "mukobi",
     "name": "Gabriel Mukobi",
     "is_organizer": True},
    upsert=True)
DB.users.update(
    {"username": "foobar"},
    {"username": "foobar",
     "name": "Unauthorized User",
     "is_organizer": False},
    upsert=True)


@app.route('/v1/authorization', methods=['POST'])
def get_authorization():
    """Finds whether the given user is authorized for edit access"""
    user = request.form.get('user_id')
    if user is None:
        return jsonify(error="You must supply a 'user_id' POST parameter!")
    authorized = is_authorized_to_edit(user)
    return jsonify(edit_access=authorized)


def is_authorized_to_edit(username):
    """
    Queries the db to find authorization of the given user
    Documents in the users collection should look like
    {"username": "cmei4444",
     "name": "Carolyn Mei",
     "is_organizer": True}
     """
    cursor = DB.users.find({"username": username})
    if cursor.count() is 0:  # user not found
        return False
    for user in cursor:
        pprint(user)
        print(user["is_organizer"])
        if user["is_organizer"]:
            return True
    return False


@app.route('/v1/', methods=['PUT'])
def add_update_user():
    """Adds or updates the user in the db and returns new user object"""
    user = request.getJSON()
    if user is None:
        # TODO(mukobi) validate the user object has everything it needs
        return jsonify(error="You must supply a valid user in the body")
    # TODO(mukobi) add or update the user in the database
    added_new_user = True
    # TODO(mukobi) get the new user object from the db to return
    user_object = {
        "user_id": "0", "username": "Dummy User", "edit_access": False
    }
    return jsonify(user_object), (201 if added_new_user else 200)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
