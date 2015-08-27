from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
from utils.mongo_json_encoder import JSONEncoder

app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
db = mongo.test_database
api = Api(app)

class Trip(Resource):
    def get(self, trip_id):
      return trips[trip_id]

    def post(self, trip_id):
      new_trip = request.json
      trips = db.trips
      result = trips.insert_one(request.json)

      trip = trips.find_one(result.inserted_id)
      print(trip) 

      return JSONEncoder().encode(trip)

api.add_resource(Trip, '/trip/<string:trip_id>')

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)

