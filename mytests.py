import unittest  # Python's built-in testing framework
from main import app  # Import the Flask app instance from your main application file

class FlaskAPITest(unittest.TestCase):
    # This method runs before each test case
    def setUp(self):
        self.client = app.test_client()  # Create a test client to simulate API requests
        self.client.testing = True       # Enable testing mode for better error messages

    # Helper method to log in and return the Authorization header
    def get_auth_header(self):
        login_data = {
            "email": "kentatech@cloud.com",
            "password": "password123"
        }
        # Send a POST request to the login endpoint
        response = self.client.post("/api/login", json=login_data)
        self.assertEqual(response.status_code, 200)  # Ensure login was successful
        token = response.get_json()["token"]         # Extract token from the response
        return {"Authorization": f"Bearer {token}"}  # Return the header with the token

    # Test user registration
    def test_register(self):
        data = {
            "username": "John Doe",
            "email": "kentatech@cloud.com",
            "password": "password123"
        }
        # Send a POST request to the register endpoint
        response = self.client.post("/api/register", json=data)
        # Expect either 201 (created) or 409 (conflict if user already exists)
        self.assertIn(response.status_code, [201, 409])
        if response.status_code == 201:
            self.assertIn("token", response.get_json())  # Token should be in the response
            print(response.get_json()["token"])          # Print token for debugging

    # Test login functionality
    def test_login(self):
        self.get_auth_header()  # Just call the helper to verify login works

    # Test GET /api/products
    def test_products(self):
        headers = self.get_auth_header()  # Get the auth header
        response = self.client.get("/api/products", headers=headers)
        self.assertEqual(response.status_code, 200)        # Expect success
        self.assertIsInstance(response.get_json(), list)   # Expect a list of products

    # Test POST /api/products
    def test_products_post(self):
        headers = self.get_auth_header()
        data = {
            "name": "Sample Product",
            "buying_price": 19.99,
            "selling_price": 29.99
        }
        response = self.client.post("/api/products", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)        # Expect product created
        self.assertIn("id", response.get_json())           # Response should include product ID

    # Test GET /api/purchases
    def test_purchases(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/purchases", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # Test POST /api/purchases
    def test_purchase_post(self):
        headers = self.get_auth_header()
        data = {
            "product_id": 1,
            "quantity": 5
        }
        response = self.client.post("/api/purchases", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    # Test GET /api/sales
    def test_sales(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/sales", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # Test POST /api/sales
    def test_sale_post(self):
        headers = self.get_auth_header()
        data = {
            "product_id": 1,
            "quantity": 2
        }
        response = self.client.post("/api/sales", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

# Run all tests when this file is executed directly
if __name__ == "__main__":
    unittest.main()