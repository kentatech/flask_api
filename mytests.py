import unittest, json
from main import app

class FlaskAPITest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_register(self):
        data = {"username" : "John Doe", "email": "kentatech@cloud.com", "password": "password123"}
        response = self.client.post("/api/register", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.get_json())
        print(response.get_json()["token"])
    
    def test_login(self):
        data = {"email": "kentatech@cloud.com", "password": "password123"}
        response = self.client.post("/api/login", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())
        print(response.get_json()["token"])
unittest.main()


