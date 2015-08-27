import os
import server
import unittest
import tempfile
import json
from pymongo import MongoClient

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
      self.app = server.app.test_client()
      # Run app in testing mode to retrieve exceptions and stack traces
      server.app.config['TESTING'] = True

      # Inject test database into application
      mongo = MongoClient('localhost', 27017)
      db = mongo.test_database
      server.app.db = db

      # Drop collection (significantly faster than dropping entire db)
      db.drop_collection('trips')

    def test_posting_trip(self):
      response = self.app.post('/trip/', 
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')
      
      responseJSON = json.loads(response.data.decode())

      assert 'application/json' in response.content_type
      assert 'Stuttgart Roadtrip' in responseJSON["name"]

    def test_getting_trip(self):
      response = self.app.post('/trip/', 
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      postResponseJSON = json.loads(response.data.decode())
      postedObjectID = postResponseJSON["_id"]

      response = self.app.get('/trip/'+postedObjectID)
      responseJSON = json.loads(response.data.decode())

      assert 'Stuttgart Roadtrip' in responseJSON["name"]

    def test_getting_all_trips(self):
      self.app.post('/trip/', 
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')
      self.app.post('/trip/', 
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      response = self.app.get('/trip/')
      responseJSON = json.loads(response.data.decode())

      self.assertEqual(len(responseJSON), 2)

if __name__ == '__main__':
    unittest.main()