import os
import logging
import requests

from flask import Flask, render_template, request, Response

app = Flask(__name__)


@app.route('/')
def index():
    user = get_user()
    is_auth = get_auth(user)
    return render_template(
        'index.html',
        auth=is_auth,
    )


def get_auth(user):
    url = os.environ.get("USER_ENDPOINT")
    r = requests.post(url, data={'user_id': user})
    response = r.json()
    is_auth = response['edit_access']
    return is_auth


def get_user():
    return "Voldemort"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
