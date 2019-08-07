"""Main flask app for pageserve service.

Serve web UI and act as an API gateway to other services.
"""

# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, render_template, request, url_for, session, redirect
from werkzeug.exceptions import BadRequestKeyError  # WSGI library for Flask

import requests

app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/v1/', methods=['GET'])
def index():
    """Displays home page with all past posts."""
    try:
        return render_template(
            'index.html',
            posts=get_posts(),
            auth=has_edit_access(get_user()),
            events=get_events(),
            app_config=app.config
        )
    except RuntimeError as error:
        return str(error), 500


@app.route('/v1/search_event', methods=['POST'])
def search_event():
    """
    Searches for the event(s) with the given name.

    Displays a page with all results if query is successful.
    """
    try:
        event_name = request.form['event_name']
        response = requests.get(app.config['EVENTS_ENDPOINT'] + 'search',
                                params={'name': event_name})
        if response.status_code == 200:
            return render_template(
                'search_results.html',
                auth=has_edit_access(get_user()),
                events=parse_events(response.json()),
                app_config=app.config
            )
        else:
            return 'Unable to retrieve events', 500
    except BadRequestKeyError as error:
        return f'Error: {error}.', 400


@app.route('/v1/query_event', methods=['GET'])
def query_event_by_id():
    """
    Queries for the event with the given ID.

    Displays a page with the result if query is successful.
    """
    try:
        event_id = request.args['event_id']
        response = requests.put(app.config['EVENTS_ENDPOINT'] + event_id)
        if response.status_code == 200:
            return render_template(
                'search_results.html',
                auth=has_edit_access(get_user()),
                events=parse_events(response.json()),
                app_config=app.config
            )
        else:
            return 'Unable to retrieve events', 500
    except BadRequestKeyError as error:
        return f'Error: {error}.', 400


@app.route('/v1/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Authenticates and proxies a request to users service to delete a post."""
    try:
        my_user_id = get_user()['user_id']
        response = requests.delete(app.config['POSTS_ENDPOINT'] + post_id,
                                   data={'author_id': my_user_id})
        return response.text, response.status_code
    except TypeError:
        return 'Error: Not signed in', 401


@app.route('/v1/events', methods=['GET'])
def show_events():
    """Displays page with all sub-events."""
    try:
        return render_template(
            'events.html',
            events=get_events(),
            auth=has_edit_access(get_user()),
            app_config=app.config
        )
    except RuntimeError as error:
        return str(error), 500


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
        gauth_token = request.form['gauth_token']
        response = authenticate_with_users_service(gauth_token)

        if response.status_code == 201:
            # authentication successful, store login in cookies
            session['user_id'] = response.json()['user_id']
            session['name'] = response.json()['name']
            session['gauth_token'] = gauth_token
        return response.content, response.status_code
    except (BadRequestKeyError, requests.exceptions.ConnectionError) as error:
        return f'Error: {error}.', 400


@app.route('/v1/sign_out', methods=['GET'])
def sign_out():
    """Sign the user out.

    Removes the 'user' object from the session.
    Redirects to the index page.
    """
    session.clear()
    return redirect(url_for('index'))


def authenticate_with_users_service(gauth_token):
    """Proxy the user service for authentication and return user object.

    Args:
        gauth_token(str): Google ID token to authenticate.

    Response:
        response: response from the users service
    """
    return requests.post(
        app.config['USERS_ENDPOINT'] + 'authenticate',
        data={'gauth_token': gauth_token})


@app.route('/v1/add_post', methods=['POST'])
def add_post():
    """Add post by calling posts service.

    Adds user id of the user making the post as author_id to form data sent to
    posts service.

    Received form data should be multipart/form-data and contain:
        event_id: id of the event to post to
        text: text content of post
        All files to be uploaded(can be multiple)

    Response:
        Redirect to index if 201 response from posts service.
        Error message and status 400 otherwise.
    """
    url = app.config['POSTS_ENDPOINT'] + 'add'
    form_data = dict(**request.form.to_dict(), author_id=get_user()['user_id'])
    response = requests.post(url, data=form_data, files=request.files)
    if response.status_code == 201:
        # upload successful, redirect to index
        return redirect(url_for("index"))
    return response.content, response.status_code


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
        Redirect to index if 201 response from events service.
        Error message and status 400 otherwise.
    """
    url = app.config['EVENTS_ENDPOINT'] + 'add'
    form_data = dict(**request.form.to_dict(), author_id=get_user()['user_id'])
    response = requests.post(url, data=form_data)
    if response.status_code == 201:
        # upload successful, redirect to index
        return redirect(url_for("index"))
    return response.content, response.status_code


def get_posts():
    """Gets all posts from posts service."""
    url = app.config['POSTS_ENDPOINT']
    response = requests.get(url, params={})
    if response.status_code == 200:
        return parse_posts(response.json())
    raise RuntimeError('Error in retrieving posts.')


def parse_posts(posts_dict):
    """Parses response from posts service to be used in HTML templates.

    Args:
        events_dict: JSON returned by posts service, includes:
            posts(list): list of posts
            num_posts(int): number of posts returned

    Returns:
        list: parsed list of posts.
    """
    # TODO(cmei4444): implement parsing on posts - timestamps are formatted
    # unreadably currently
    return posts_dict['posts']


def get_events():
    """Gets all sub-events from events service."""
    url = app.config['EVENTS_ENDPOINT']
    response = requests.get(url, params={})
    if response.status_code == 200:
        return parse_events(response.json())
    raise RuntimeError('Error in retrieving events.')


def parse_events(events_dict):
    """Parses response from events service to be used in HTML templates.

    Args:
        events_dict: JSON returned by events service, includes:
            events(list): list of events
            num_events(int): number of events returned

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
    url = app.config['USERS_ENDPOINT'] + 'authorization'
    response = requests.post(url, data={'user_id': user['user_id']})
    return response.json()['edit_access'] is True


def get_user():
    """Retrieves the current user of the app or None if not signed in."""
    try:
        if 'gauth_token' in session:
            response = authenticate_with_users_service(
                session['gauth_token'])
            if response.status_code == 201:
                return response.json()
        return None  # Not signed in
    except requests.exceptions.ConnectionError:
        return None  # Can't connect to users service


# set GAuth callback to the route defined by the authenticate() function
with app.test_request_context():
    app.config['GAUTH_CALLBACK_ENDPOINT'] = url_for(
        'authenticate_and_get_user')


def config_endpoints(endpoints):
    """Sets given list of endpoints globally from environment variables.

    Throws a NameError if any endpoint is not found."""
    for endpoint in endpoints:
        if endpoint in os.environ:
            app.config[endpoint] = os.environ.get(endpoint)
        else:
            raise NameError('Endpoint {} not defined.'.format(endpoint))


config_endpoints(['USERS_ENDPOINT', 'EVENTS_ENDPOINT', 'POSTS_ENDPOINT'])

app.config['GAUTH_CLIENT_ID'] = os.environ.get('GAUTH_CLIENT_ID')
app.config['GAUTH_CALLBACK_ENDPOINT'] = (app.config['USERS_ENDPOINT']
                                         + 'authenticate')

# set flask secret key used for session encryption
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

if __name__ == '__main__':    # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
