import os
import logging
import requests

from flask import Flask, render_template, request, Response

app = Flask(__name__)


@app.route('/v1/add', methods=['POST'])
def add_event():
    pass


@app.route('/v1/edit', methods=['POST'])
def edit_event():
    pass


@app.route('/v1/', methods=['GET'])
def get_all_events():
    pass


@app.route('/v1/search', methods=['GET'])
def search_event():
    pass


@app.route('/v1/<event-id>', methods=['PUT'])
def get_one_event():
    pass
