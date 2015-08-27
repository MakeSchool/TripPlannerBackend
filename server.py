from flask import Flask, request
from flask_restful import Resource, Api
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)
api = Api(app)

trips = {}

class Trip(Resource):
    def get(self, trip_id):
        return trips[trip_id]

    def post(self, trip_id):
      trips[trip_id] = request.json
      
      return request.json

api.add_resource(Trip, '/trip/<string:trip_id>')

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)