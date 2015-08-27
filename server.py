from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)

api = Api(app)

trips = {}

class Trip(Resource):
    def get(self, trip_id):
        return {trips[trip_id]}

    def post(self, trip_id):
        trips[trip_id] = request.form['data']
        return {trip_id: trips[trip_id]}

api.add_resource(Trip, '/trip/<string:trip_id>')

if __name__ == '__main__':
    app.run(debug=True)
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True