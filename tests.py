import os
import server
import unittest
import tempfile
import json

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
      self.app = server.app.test_client()
      print("setup")

    def tearDown(self):
      print("teardown")

    def test_posting_trip(self):
      response = self.app.post('/trip/1', 
        data=json.dumps(dict(
          name="Stuttgart Roadtrip"
        )), 
        content_type = 'application/json')

      print(response.data.decode())

      assert 'Stuttgart Roadtrip' in response.data.decode()

    def test_getting_trip(self):
      response = self.app.get('/trip/1')

      print(response.data.decode())

      assert 'Stuttgart Roadtrip' in response.data.decode()


if __name__ == '__main__':
    unittest.main()