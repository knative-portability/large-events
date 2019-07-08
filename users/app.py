import os

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World from the users service!'

@app.route('/v1/users/authorization', methods=['GET'])
def find_authorization():
    user = request.args.get('user_id')
    if user == None:
        return jsonify(error="You must supply a 'user_id' parameter!")
    else:
        authorized = user != 'Voldemort'
        return jsonify(edit_access=authorized)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))