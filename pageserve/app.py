import os
import logging
import requests

from flask import Flask, render_template, request, Response

app = Flask(__name__)


@app.route('/v1/')
def index():
    user = get_user()
    is_auth = get_auth(user)
    posts = get_posts()
    return render_template(
        'index.html',
        posts=posts,
        auth=is_auth,
    )


@app.route('/v1/events')
def show_events():
    user = get_user()
    auth = has_edit_access(get_auth_json(user))
    events = get_events()
    return render_template(
        'events.html',
        events=events,
        auth=is_auth,
    )


def get_posts():
    # TODO: integrate with posts service to pull post info from database
    return [{'post_id': '1', 'event_id': '0', 'type': 'text', 'author': 'admin',
             'created_at': '7-9-2019', 'text': 'this will be a fun event!',
             },
            {'post_id': '2', 'event_id': '0', 'type': 'image', 'author': 'admin',
             'created_at': '7-9-2019', 'text': 'abcdefghi',
             }]


def get_events():
    # TODO(mcarolyn): integrate with events service to pull event info from
    # database
    return [{'event_id': '1', 'name': 'concert 1', 'description': 'listen to fun music here!',
             'author': 'admin', 'created_at': '7-9-2019', 'event_time': '7-10-2019',
             },
            {'event_id': '2', 'name': 'concert 2', 'description': 'listen to fun music here!',
             'author': 'admin', 'created_at': '7-9-2019', 'event_time': '7-12-2019',
             }]


def get_auth_json(user):
    url = os.environ.get("USER_ENDPOINT")
    r = requests.post(url, data={'user_id': user})
    response = r.json()
    return response


def has_edit_access(user_data):
    return user_data['edit_access']


def get_user():
    # TODO: get user info using OAuth
    return "Voldemort"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
