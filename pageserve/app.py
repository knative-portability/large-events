"""
Copyright 2019 The Knative Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from flask import Flask, render_template, request, url_for, session, redirect
from werkzeug.exceptions import BadRequestKeyError  # WSGI library for Flask

import requests

app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/v1/', methods=['GET'])
def index():
    """Displays home page with all past posts."""
    posts = get_posts()
    return render_template(
        'index.html',
        posts=posts,
        auth=has_edit_access(get_user()),
        app_config=app.config
    )


@app.route('/v1/events', methods=['GET'])
def show_events():
    """Displays page with all sub-events."""
    events = get_events()
    return render_template(
        'events.html',
        events=events,
        auth=has_edit_access(get_user()),
        app_config=app.config
    )


@app.route('/v1/authenticate', methods=['POST'])
def authenticate_and_get_user():
    """Proxy for user authentication service.

    Call the users service to verify user authentication token and
    upload user profile to users db.

    On successful authentication, stores user info in the session.

    Request data:
        gauth_token: Google ID token to authenticate.

    Response:
        Response:
            201: user object from the db if authentication was successful.
            400: error message if authentication was not successful.
    """
    try:
        gauth_token = request.form["gauth_token"]
        response = authenticate_with_users_service(gauth_token)

        if response.status_code == 201:
            # authentication successful, store login in cookies
            session["user_id"] = response.json()["user_id"]
            session["name"] = response.json()["name"]
            session["gauth_token"] = gauth_token
        return response.content, response.status_code
    except BadRequestKeyError as error:
        return f"Error: {error}.", 400


@app.route('/v1/sign_out', methods=['GET'])
def sign_out():
    """Sign the user out.

    Removes the 'user' object from the session.
    Redirects to the index page.
    """
    session.clear()
    return redirect(url_for("index"))


def authenticate_with_users_service(gauth_token):
    """Proxy the user service for authentication and return user object.

    Args:
        gauth_token (str): Google ID token to authenticate.

    Response:
        response: response from the users service
    """
    return requests.post(
        app.config["USERS_ENDPOINT"] + "authenticate",
        data={"gauth_token": gauth_token})


@app.route('/v1/add_post', methods=['POST'])
def add_post():
    """Add post by calling posts service.

    Adds user id of the user making the post as author_id to form data sent to
    posts service.

    Received form data should be multipart/form-data and contain:
        event_id: id of the event to post to
        text: text content of post
        All files to be uploaded (can be multiple)

    Response:
        string response and response code returned by posts service
    """
    url = app.config['POSTS_ENDPOINT'] + 'add'
    form_data = dict(**request.form.to_dict(), author_id=get_user())
    r = requests.post(url, data=form_data)
    return r.content, r.status_code


@app.route('/v1/add_event', methods=['POST'])
def add_event():
    """Add event by calling events service.

    Adds user id of the user creating the event as author_id to form data sent
    to events service.

    Received form data should contain:
        event_name: name of the created event
        description: description of event
        event_time: time of event

    Response:
        string response and response code returned by events service
    """
    url = app.config['EVENTS_ENDPOINT'] + 'add'
    form_data = dict(**request.form.to_dict(), author_id=get_user())
    r = requests.post(url, data=form_data)
    return r.content, r.status_code


def get_posts():
    """Gets all posts from posts service."""
    # TODO: integrate with posts service to pull post info from database
    posts = [{'post_id': '1',
              'event_id': '0',
              'type': 'text',
              'author': 'admin',
              'created_at': '7-9-2019',
              'text': 'this will be a fun event!',
              },
             {'post_id': '2',
              'event_id': '0',
              'type': 'image',
              'author': 'admin',
              'created_at': '7-9-2019',
              'text': 'abcdefghi',
              }]
    return parse_posts(posts)


def parse_posts(posts):
    # TODO(cmei4444): implement parsing on posts pulled from posts service in
    # a format for web display
    return posts


def get_events():
    """Gets all sub-events from events service."""
    url = app.config['EVENTS_ENDPOINT']
    r = requests.get(url, params={})
    if r.status_code == 200:
        return parse_events(r.json())
    else:
        # TODO(cmei4444): handle error in a way that doesn't break page display
        return "Error in getting events"


def parse_events(events_dict):
    """Parses response from events service to be used in HTML templates.

    Args:
        events_dict: JSON returned by events service, includes:
            events (list): list of events
            num_events (int): number of events returned

    Returns:
        list: parsed list of events.
    """
    # TODO(cmei4444): implement parsing on events - timestamps are formatted
    # unreadably currently
    return events_dict['events']


def has_edit_access(user):
    """Determines if the user with the given info has edit access."""
    if user is None:
        return False
    url = app.config["USERS_ENDPOINT"] + "authorization"
    response = requests.post(url, data={"user_id": user["user_id"]})
    return bool(response.json()["edit_access"]) if user else False


def get_user():
    """Retrieves the current user of the app or None if not signed in."""
    if "gauth_token" in session:
        response = authenticate_with_users_service(
            session["gauth_token"])
        if response.status_code == 201:
            return response.json()
    return None  # Not signed in


# set GAuth callback to the route defined by the authenticate() function
with app.test_request_context():
    app.config["GAUTH_CALLBACK_ENDPOINT"] = url_for(
        "authenticate_and_get_user")


def config_endpoints(endpoints):
    """Sets given list of endpoints globally from environment variables.

    Throws a NameError if any endpoint is not found."""
    for endpoint in endpoints:
        if endpoint in os.environ:
            app.config[endpoint] = os.environ.get(endpoint)
        else:
            raise NameError("Endpoint {} not defined.".format(endpoint))


config_endpoints(['USERS_ENDPOINT', 'EVENTS_ENDPOINT'])

app.config["GAUTH_CLIENT_ID"] = os.environ.get("GAUTH_CLIENT_ID")
app.config["GAUTH_CALLBACK_ENDPOINT"] = (app.config['USERS_ENDPOINT']
                                         + "authenticate")

# set flask secret key used for session encryption
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if __name__ == "__main__":    # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
