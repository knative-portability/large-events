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
import logging
import requests

from flask import Flask, render_template, request, Response

app = Flask(__name__)


@app.route('/')
def index():
    user = get_user()
    is_auth = has_edit_access(get_auth_json(user))
    posts = get_posts()
    return render_template(
        'index.html',
        auth=is_auth,
    )


@app.route('/v1/events')
def show_events():
    user = get_user()
    is_auth = has_edit_access(get_auth_json(user))
    events = get_events()
    return render_template(
        'events.html',
        events=events,
        auth=is_auth,
    )


def get_posts():
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
    return parsed_posts(posts)


def parsed_posts(posts):
    return posts


def get_events():
    # TODO(mcarolyn): integrate with events service to pull event info from
    # database
    events = [{'event_id': '1',
               'name': 'concert 1',
               'description': 'listen to fun music here!',
               'author': 'admin',
               'created_at': '7-9-2019',
               'event_time': '7-10-2019',
               },
              {'event_id': '2',
               'name': 'concert 2',
               'description': 'listen to fun music here!',
               'author': 'admin',
               'created_at': '7-9-2019',
               'event_time': '7-12-2019',
               }]
    return parsed_events(events)


def parsed_events(events):
    return events


def get_auth_json(user):
    url = os.environ.get("USER_ENDPOINT")
    r = requests.post(url, data={'user_id': user})
    response = r.json()
    is_auth = response['edit_access']
    return is_auth


def get_user():
    return "Voldemort"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
