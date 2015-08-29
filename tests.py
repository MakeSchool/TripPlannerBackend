import os
import server
import unittest
import tempfile
import json
import base64
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
        headers=self.generate_auth_header('admin', 'secret'),
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')
      
      responseJSON = json.loads(response.data.decode())

      self.assertEqual(response.status_code, 200)
      assert 'application/json' in response.content_type
      assert 'Stuttgart Roadtrip' in responseJSON["name"]

    def test_getting_trip(self):
      response = self.app.post('/trip/', 
        headers=self.generate_auth_header('admin', 'secret'),
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      postResponseJSON = json.loads(response.data.decode())
      postedObjectID = postResponseJSON["_id"]

      response = self.app.get('/trip/'+postedObjectID,
          headers=self.generate_auth_header('admin', 'secret')
        )
      responseJSON = json.loads(response.data.decode())

      self.assertEqual(response.status_code, 200)
      assert 'Stuttgart Roadtrip' in responseJSON["name"]

    def test_getting_all_trips(self):
      self.app.post('/trip/', 
        headers=self.generate_auth_header('admin', 'secret'),
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      self.app.post('/trip/', 
        headers=self.generate_auth_header('admin', 'secret'),
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      response = self.app.get('/trip/',
          headers=self.generate_auth_header('admin', 'secret')
        )
      responseJSON = json.loads(response.data.decode())

      self.assertEqual(response.status_code, 200)
      self.assertEqual(len(responseJSON), 2)


    def generate_auth_header(self, username, password):
      authString = username + ":" + password
      return {'Authorization': 'Basic ' + base64.b64encode(authString.encode('utf-8')).decode('utf-8') }

if __name__ == '__main__':
    unittest.main()