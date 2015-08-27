from flask import Flask, request, make_response
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
from utils.mongo_json_encoder import JSONEncoder
from bson.objectid import ObjectId

app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
db = mongo.test_database
api = Api(app)

class Trip(Resource):
    def get(self, trip_id):
      trips = db.trips
      trip = trips.find_one({'_id': ObjectId(trip_id)})
      return trip

    def post(self):
      new_trip = request.json
      trips = db.trips
      result = trips.insert_one(request.json)

      trip = trips.find_one(result.inserted_id)

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