import server
import unittest
import json
import base64
from pymongo import MongoClient

db = None


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        global db
        db = mongo.test_database
        server.app.db = db

        # Reduce encryption workloads for tests
        server.app.bcrypt_rounds = 4

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('trips')

        self.app.post('/user/',
                      data=json.dumps(dict(
                          username="user",
                          password="password"
                      )),
                      content_type='application/json')

    @classmethod
    def tearDownClass(cls):
        db.drop_collection('users')

    # User tests

    def test_signup_with_username_and_password(self):
        response = self.app.post('/user/',
                                 data=json.dumps(dict(
                                     username="benjamin",
                                     password="test"
                                 )),
                                 content_type='application/json')

        json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)

    def test_verifying_credentials(self):
        self.app.post('/user/',
                      data=json.dumps(dict(
                          username="benjamin",
                          password="test"
                      )),
                      content_type='application/json')

        response = self.app.get('/user/',
                                headers=self.default_auth_header()
                                )

        self.assertEqual(response.status_code, 200)

    def test_incorrect_credentials(self):
        response = self.app.get('/user/',
                                headers=self.generate_auth_header(
                                    'wrongusername', 'andpassword')
                                )

        self.assertEqual(response.status_code, 401)

    # Trip tests

    def test_posting_trip(self):
        response = self.app.post('/trip/',
                                 headers=self.default_auth_header(),
                                 data=json.dumps(dict(
                                     name="Stuttgart Roadtrip"
                                 )),
                                 content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'Stuttgart Roadtrip' in responseJSON["name"]
        assert 'user' in responseJSON["user"]

    def test_unauthorized_request(self):
        response = self.app.post('/trip/',
                                 data=json.dumps(dict(
                                     name="Stuttgart Roadtrip"
                                 )),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_getting_trip(self):
        response = self.app.post('/trip/',
                                 headers=self.default_auth_header(),
                                 data=json.dumps(dict(
                                     name="Stuttgart Roadtrip"
                                 )),
                                 content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trip/' + postedObjectID,
                                headers=self.default_auth_header()
                                )
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Stuttgart Roadtrip' in responseJSON["name"]

    def test_getting_all_trips(self):
        self.app.post('/trip/',
                      headers=self.default_auth_header(),
                      data=json.dumps(dict(
                          name="Stuttgart Roadtrip"
                      )),
                      content_type='application/json')

        self.app.post('/trip/',
                      headers=self.default_auth_header(),
                      data=json.dumps(dict(
                          name="Stuttgart Roadtrip"
                      )),
                      content_type='application/json')

        response = self.app.get('/trip/',
                                headers=self.default_auth_header()
                                )
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(responseJSON), 2)

    def test_getting_all_trips_is_user_specific(self):
        self.app.post('/trip/',
                      headers=self.default_auth_header(),
                      data=json.dumps(dict(
                          name="Stuttgart Roadtrip"
                      )),
                      content_type='application/json')

        self.app.post('/user/',
                      data=json.dumps(dict(
                          username="user2",
                          password="test"
                      )),
                      content_type='application/json')

        self.app.post('/trip/',
                      headers=self.generate_auth_header('user2', 'test'),
                      data=json.dumps(dict(
                          name="Stuttgart Roadtrip"
                      )),
                      content_type='application/json')

        responseUser1 = self.app.get('/trip/',
                                     headers=self.default_auth_header()
                                     )
        responseUser1JSON = json.loads(responseUser1.data.decode())

        responseUser2 = self.app.get('/trip/',
                                     headers=self.generate_auth_header(
                                         'user2', 'test'),
                                     )
        responseUser2JSON = json.loads(responseUser2.data.decode())

        self.assertEqual(responseUser1.status_code, 200)
        self.assertEqual(len(responseUser1JSON), 1)

        self.assertEqual(responseUser2.status_code, 200)
        self.assertEqual(len(responseUser2JSON), 1)

    def test_deleting_trip_returns_trip_identifier(self):
        response = self.app.post('/trip/',
                                 headers=self.default_auth_header(),
                                 data=json.dumps(dict(
                                     name="Stuttgart Roadtrip"
                                 )),
                                 content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trip/' + postedObjectID,
                                   headers=self.default_auth_header()
                                   )
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert postedObjectID in responseJSON["tripIdentifier"]

    def test_updating_trip_returns(self):
        response = self.app.post('/trip/',
                                 headers=self.default_auth_header(),
                                 data=json.dumps(dict(
                                     name="Stuttgart Roadtrip"
                                 )),
                                 content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.put('/trip/' + postedObjectID,
                                headers=self.default_auth_header(),
                                data=json.dumps(dict(
                                    name="San Francisco Roadtrip"
                                )),
                                content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert "San Francisco" in responseJSON["name"]

    def default_auth_header(self):
        return self.generate_auth_header("user", "password")

    def generate_auth_header(self, username, password):
        authString = username + ":" + password
        return {'Authorization': 'Basic ' +
                base64.b64encode(authString.encode('utf-8')).decode('utf-8')}

if __name__ == '__main__':
    unittest.main()
