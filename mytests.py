
# Import Python's built-in unit testing framework
import unittest

# Import Flask app instance from main.py
from main import app

# Create a test class inheriting from unittest.TestCase
class FlaskAPITest(unittest.TestCase):

    # ----------------------------
    # Runs before every test
    # ----------------------------
    def setUp(self):
        # Create a test client to simulate HTTP requests
        self.client = app.test_client()
        # Enable testing mode for clearer error messages
        self.client.testing = True

    # ----------------------------
    # Helper: log in and get JWT header
    # ----------------------------
    def get_auth_header(self):
        login_data = {
            "email": "kentatech@cloud.com",
            "password": "password123"
        }

        # Send POST request to /api/login with login credentials
        response = self.client.post("/api/login", json=login_data)

        # Ensure login succeeded
        self.assertEqual(response.status_code, 200)

        # Extract JWT token from JSON response
        token = response.get_json()["token"]

        # Return header with token for protected routes
        return {"Authorization": f"Bearer {token}"}

    # ----------------------------
    # Test: User registration
    # ----------------------------
    def test_register(self):
        data = {
            "username": "John Doe",
            "email": "kentatech@cloud.com",
            "password": "password123"
        }

        # POST request to register endpoint
        response = self.client.post("/api/register", json=data)

        # Status should be 201 (created) or 409 (already exists)
        self.assertIn(response.status_code, [201, 409])

        if response.status_code == 201:
            # Newly created user should have a token
            self.assertIn("token", response.get_json())

    # ----------------------------
    # Test: Login
    # ----------------------------
    def test_login(self):
        # Call helper to verify login works
        self.get_auth_header()

    # ----------------------------
    # Test: GET /api/products
    # ----------------------------
    def test_products_get(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/products", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # ----------------------------
    # Test: POST /api/products
    # ----------------------------
    def test_products_post(self):
        headers = self.get_auth_header()
        data = {
            "name": "Test Product",
            "buying_price": 10.5,
            "selling_price": 15.5
        }
        response = self.client.post("/api/products", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    # ----------------------------
    # Test: GET /api/purchases
    # ----------------------------
    def test_purchases_get(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/purchases", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # ----------------------------
    # Test: POST /api/purchases
    # ----------------------------
    def test_purchase_post(self):
        headers = self.get_auth_header()
        data = {
            "product_id": 1,
            "quantity": 5
        }
        response = self.client.post("/api/purchases", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    # ----------------------------
    # Test: GET /api/sales
    # ----------------------------
    def test_sales_get(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/sales", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # ----------------------------
    # Test: POST single sale
    # ----------------------------
    def test_sale_post_single(self):
        headers = self.get_auth_header()
        data = {
            "product_id": 1,
            "quantity": 2
        }

        # POST a single sale
        response = self.client.post("/api/sales", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)

        # Extract response JSON
        json_data = response.get_json()
        self.assertIn("id", json_data)
        self.assertIn("product_id", json_data)
        self.assertIn("quantity", json_data)

        # ----------------------------
        # Explanation for beginners:
        # db.session.flush() is called in main.py before committing.
        # This ensures the new Sale gets an ID, so we can add SalesDetails using that ID.
        # db.session.commit() then saves everything permanently to the database.
        # ----------------------------

    # ----------------------------
    # Test: POST multiple sales (bulk)
    # ----------------------------
    def test_sale_post_bulk(self):
        headers = self.get_auth_header()
        data = {
            "items": [
                {"product_id": 1, "quantity": 1},
                {"product_id": 1, "quantity": 1}
            ]
        }

        response = self.client.post("/api/sales", json=data, headers=headers)
        self.assertEqual(response.status_code, 201)

        json_data = response.get_json()
        self.assertIn("sale_id", json_data)
        self.assertIn("items", json_data)
        self.assertEqual(len(json_data["items"]), 2)

        # ----------------------------
        # Explanation:
        # Bulk sales handle multiple products in one transaction.
        # Each item is checked for stock before adding SalesDetails.
        # commit() saves all sale details at once.
        # ----------------------------

    # ----------------------------
    # Test: GET /api/stock
    # ----------------------------
    def test_stock_summary(self):
        # This endpoint does not require JWT
        response = self.client.get("/api/stock")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # ----------------------------
    # Test: GET /api/dashboard
    # ----------------------------
    def test_dashboard(self):
        headers = self.get_auth_header()
        response = self.client.get("/api/dashboard", headers=headers)
        self.assertEqual(response.status_code, 200)

        # Dashboard returns multiple charts, check for keys
        json_data = response.get_json()
        expected_keys = ["data", "labels", "sales_labels", "sales_data", "donut_data", "donut_label"]
        for key in expected_keys:
            self.assertIn(key, json_data)

    # ----------------------------
    # Test: POST /api/logout
    # ----------------------------
    def test_logout(self):
        headers = self.get_auth_header()
        response = self.client.post("/api/logout", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())


# ----------------------------
# Run tests when this file is executed
# ----------------------------
if __name__ == "__main__":
    unittest.main()

"""
===========================================
Flask API Unit Tests (Beginner-Friendly)
===========================================

This file contains all tests for your Flask API. It is fully commented for junior developers.

Comment Dictionary (Common Keywords Used in this File):
-------------------------------------------------------
1. app.test_client(): Creates a simulated client to send requests to Flask routes without running the server.
2. self.client.get/post(): Simulate GET or POST requests.
3. JWT / token: JSON Web Token used to access protected routes. Generated after login/register.
4. headers={"Authorization": "Bearer <token>"}: Used to include JWT in API requests.
5. db.session.commit(): Saves changes to the database permanently.
6. db.session.flush(): Assigns IDs to new objects without committing; used to reference them in the same session.
7. assertEqual(a, b): Checks if a == b in tests.
8. assertIn(a, b): Checks if a exists inside b.
9. assertIsInstance(obj, type): Checks if obj is of a specific type.
10. response.get_json(): Converts Flask response to Python dictionary/list.
11. setUp(): Runs before every test to prepare the environment.
12. tearDown(): (Optional) runs after each test to clean up.
"""
