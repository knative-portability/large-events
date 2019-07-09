"""
users/app.py
Authors: mukobi
Main flask app for users service
    - adding/updating users in the users db
    - getting the authorization level of a user
"""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/v1/authorization', methods=['GET'])
def get_authorization():
    """Finds whether the given user is authorized for edit access"""
    user = request.args.get('user_id')
    if user is None:
        return jsonify(error="You must supply a 'user_id' GET parameter!")
    authorized = is_authorized_to_edit(user, None)
    return jsonify(edit_access=authorized)


def is_authorized_to_edit(user, database):
    """Queries the db to find authorization of the given user"""
    # TODO(mukobi) query db for actual user authorization
    return user != 'Voldemort'


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
