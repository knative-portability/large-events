import os
import logging
import pymongo
# import pprint

from flask import Flask, request, Response

app = Flask(__name__)

# connect to MongoDB Atlas database
MONGODB_ATLAS_USERNAME = os.environ.get(
    "MONGODB_ATLAS_USERNAME")
MONGODB_ATLAS_PASSWORD = os.environ.get(
    "MONGODB_ATLAS_PASSWORD")
MONGODB_ATLAS_CLUSTER_ADDRESS = os.environ.get(
    "MONGODB_ATLAS_CLUSTER_ADDRESS")
PYMONGO_URI = "mongodb+srv://{}:{}@{}".format(
    MONGODB_ATLAS_USERNAME,
    MONGODB_ATLAS_PASSWORD,
    MONGODB_ATLAS_CLUSTER_ADDRESS)
# print("Pymongo URI: {}".format(PYMONGO_URI))
client = pymongo.MongoClient(PYMONGO_URI)
testDB = client.test
eventsDB = client.eventsDB
events_coll = eventsDB.all_events


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


@app.route('/v1/<event_id>', methods=['PUT'])
def get_one_event(event_id):
    pass

class Event(object):
    attributes = ['event_id', 'name', 'description', 'author', 'created_at', 'event_time']

    def __init__(self, info):
        self.info = info

    def __eq__(self, other):
        """Determines if two events have the same information"""
        for att in attributes:
            if self.info[att] != other.info[att]:
                return False
        return True

    def is_valid(self):
        """Checks to make sure all of the required attributes are in the event info"""
        for att in attributes:
            if att not in self.info:
                return False
        return True
