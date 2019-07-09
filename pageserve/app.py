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
#    url = "users_endpoint"
#    r = requests.post('https://httpbin.org/post', data={'user_id':user})
#    response = r.json()
#    is_auth = response['edit_access']
    return True

def get_user():
    return "carolyn"
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
