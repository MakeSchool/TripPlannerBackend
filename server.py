from flask import Flask, request, make_response, Response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
from utils.mongo_json_encoder import JSONEncoder
from bson.objectid import ObjectId
from functools import wraps

app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {'message': "Basic Auth Required."}
            resp = jsonify(message)
            resp.status_code = 401

            return resp
        return f(*args, **kwargs)
    return decorated

class Trip(Resource):

    @requires_auth
    def get(self, trip_id = None):
      if trip_id is None:
        trip_collection = app.db.trips
        trips = list(trip_collection.find())
        return trips
      else:
        trip_collection = app.db.trips
        trip = trip_collection.find_one({'_id': ObjectId(trip_id)})
        return trip

    @requires_auth
    def post(self):
      new_trip = request.json
      trip_collection = app.db.trips
      result = trip_collection.insert_one(request.json)

      trip = trip_collection.find_one(result.inserted_id)

      return trip

api.add_resource(Trip, '/trip/','/trip/<string:trip_id>')

# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)