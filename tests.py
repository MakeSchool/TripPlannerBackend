import os
import server
import unittest
import tempfile
import json

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
      self.app = server.app.test_client()
      server.app.config['TESTING'] = True
      print("setup")

    def tearDown(self):
      print("teardown")

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

      responseJSON = json.loads(response.data.decode())
      postedObjectID = responseJSON["_id"]

      response = self.app.get('/trip/'+postedObjectID)
      responseJSON = json.loads(response.data.decode())

      assert 'Stuttgart Roadtrip' in responseJSON["name"]


if __name__ == '__main__':
    unittest.main()