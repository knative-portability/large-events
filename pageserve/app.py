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
import requests

from flask import Flask, render_template, request, Response

app = Flask(__name__)  # pylint: disable=invalid-name


@app.route('/v1/', methods=['GET'])
def index():
    """Displays home page with all past posts."""
    user = get_user()
    is_auth = has_edit_access(get_user_info(user,
                                            app.config['USERS_ENDPOINT']
                                            + "authorization"))
    posts = get_posts()
    return render_template(
        'index.html',
        posts=posts,
        auth=is_auth,
        user=user,
        app_config=app.config
    )


@app.route('/v1/events', methods=['GET'])
def show_events():
    """Displays page with all sub-events."""
    user = get_user()
    is_auth = has_edit_access(get_user_info(user,
                                            app.config['USERS_ENDPOINT']
                                            + "authorization"))
    events = get_events()
    return render_template(
        'events.html',
        events=events,
        auth=is_auth,
        user=user,
        app_config=app.config
    )


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
        String response and response code returned by posts service:
            201 if post added successfully
            400 if post info is malformatted
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
        String response and response code returned by posts service:
            201 if event added successfully
            400 if event info is malformatted
    """
    url = app.config['EVENTS_ENDPOINT'] + 'add'
    form_data = dict(**request.form.to_dict(), author_id=get_user())
    r = requests.post(url, data=form_data)
    return r.content, r.status_code


def get_posts():
    """Gets all posts from posts service."""
    url = app.config['POSTS_ENDPOINT']
    r = requests.get(url, params={})
    if r.status_code == 200:
        return parse_posts(r.json())
    else:
        # TODO(cmei4444): handle error in a way that doesn't break page display
        return "Error in getting posts"


def parse_posts(posts_dict):
    """Parses response from posts service to be used in HTML templates.

    Args:
        events_dict: JSON returned by posts service, includes:
            posts (list): list of posts
            num_posts (int): number of posts returned

    Returns:
        list: parsed list of posts.
    """
    # TODO(cmei4444): implement parsing on posts - timestamps are formatted
    # unreadably currently
    return posts_dict['posts']


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


def get_user_info(user, url):
    """Gets info about the current user from the users service."""
    r = requests.post(url, data={'user_id': user})
    response = r.json()
    return response


def has_edit_access(user_data):
    """Determines if the user with the given info has edit access."""
    return user_data['edit_access']


def get_user():
    """Retrieves the current user of the app."""
    # TODO: get user info using OAuth
    return "Voldemort"


def config_endpoints(endpoints):
    """Sets given list of endpoints globally from environment variables.

    Throws a NameError if any endpoint is not found."""
    for endpoint in endpoints:
        if endpoint in os.environ:
            app.config[endpoint] = os.environ.get(endpoint)
        else:
            raise NameError("Endpoint {} not defined.".format(endpoint))


config_endpoints(['USERS_ENDPOINT', 'EVENTS_ENDPOINT', 'POSTS_ENDPOINT'])

app.config["GAUTH_CLIENT_ID"] = os.environ.get("GAUTH_CLIENT_ID")
app.config["GAUTH_CALLBACK_ENDPOINT"] = (app.config['USERS_ENDPOINT']
                                         + "authenticate")

if __name__ == "__main__":    # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
