"""
users/app.py
Authors: mukobi
Main flask app for users service
    - adding/updating users in the users db
    - getting the authorization level of a user
"""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello from the users service. Go to <a href='/v1/authorization?user_id=you_user_id_here'>/v1/authorization?user_id=you_user_id_here</a> to test."

@app.route('/v1/authorization', methods=['GET'])
def get_authorization():
    """Finds whether the given user is authorized for edit access"""
    user = request.args.get('user_id')
    if user == None:
        return jsonify(error="You must supply a 'user_id' GET parameter!")
    else:
        authorized = user != 'Voldemort'
        return jsonify(edit_access=authorized)

@app.route('/v1/', methods=['PUT'])
def add_update_user():
    """Adds or updates the user in the db and returns new user object"""
    user = request.getJSON()
    if user == None:
        # TODO(mukobi) validate the user object has everything it needs
        return jsonify(error="You must supply a valid user in the body")
    else:
        # TODO(mukobi) add or update the user in the database 
        added_new_user = True
        # TODO(mukobi) get the new user object from the db to return 
        user_object = {
            "user_id": "0", "username": "Dummy User", "edit_access": False
        }
        return jsonify(user_object), (201 if added_new_user else 200)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
