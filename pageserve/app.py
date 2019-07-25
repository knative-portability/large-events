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

app = Flask(__name__)


def config_endpoints(endpoints):
    """Sets given list of endpoints globally from environment variables.

    Throws a NameError if any endpoint is not found."""
    for endpoint in endpoints:
        if endpoint in os.environ:
            app.config[endpoint] = os.environ.get(endpoint)
        else:
            raise NameError("Endpoint {} not defined.".format(endpoint))


config_endpoints(['USERS_ENDPOINT', 'EVENTS_ENDPOINT'])


@app.route('/v1/')
def index():
    """Displays home page with all past posts."""
    user = get_user()
    is_auth = has_edit_access(get_user_info(user,
                                            app.config['USERS_ENDPOINT']))
    posts = get_posts()
    return render_template(
        'index.html',
        posts=posts,
        auth=is_auth,
    )


@app.route('/v1/events')
def show_events():
    """Displays page with all sub-events."""
    user = get_user()
    is_auth = has_edit_access(get_user_info(user,
                                            app.config['USERS_ENDPOINT']))
    events = get_events()
    return render_template(
        'events.html',
        events=events,
        auth=is_auth,
    )


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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
