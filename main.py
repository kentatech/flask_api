from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import sentry_sdk

# Initialize Sentry for error tracking and performance monitoring
sentry_sdk.init(
    dsn="https://b9209a4599b4a4a133ee86ab3e929af9@o4510040530550784.ingest.de.sentry.io/4510040591892560",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Enable sending logs to Sentry
    enable_logs=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)

# Send logs directly to Sentry
# sentry_sdk.logger.info('This is an info log message')
# sentry_sdk.logger.warning('This is a warning message')
# sentry_sdk.logger.error('This is an error message')

app = Flask(__name__)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a random secret key in production



products_list = []
sales_list = []
purchases_list = []
users_list = []


def is_int(value):
    try:
        int(value)
        return True
    except(ValueError, TypeError):
        return False
    
def is_number(value):
    try:
        float(value)
        return True
    except(ValueError, TypeError):
        return False

@app.route("/",methods=['GET'])
def home():
     res = {"flask api version": "1.0.0"}
     return jsonify(res), 200

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if "name" not in data.keys() or "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
        #Elif expected to check mail is valid/exists, password is long, fields not empty

    else:
        users_list.append(data)
        #create JWT token
        token = create_access_token(identity=data["email"])
        return jsonify({"token": token}), 201
    
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
    else:
        for user in users_list:
            if user["email"] == data["email"] and user["password"] == data["password"]:
                #create JWT token
                token = create_access_token(identity = data["email"])
    
                return jsonify({"token":token}), 200
            else:
                 pass
        error = {"error": "Invalid email or password"}
        return jsonify(error), 401

@app.route("/api/users")
def get_users():
    return jsonify(users_list), 200

@app.route('/api/products', methods=['GET', 'POST'])
@jwt_required()
def products():
    if request.method == 'GET':
        # Logic to retrieve products
        return jsonify(products_list), 200
    elif request.method == 'POST':
        data =request.get_json()
        if 'name' not in data or 'buying_price' not in data.keys() or 'selling_price' not in data.keys():
            error = {"error" : "ensure all fields are filled"}
            return jsonify(error), 400
        else:
            products_list.append(data)
            return jsonify(data),201
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405
    
    
@app.route("/api/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    if request.method == "GET":
        return jsonify(sales_list), 200
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must be in json"}), 400
        
        if "product_id" not in data or "quantity" not in data:
            return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
        
@app.route("/api/purchases", methods=["GET", "POST"])
@jwt_required()
def purchases():
    if request.method == "GET":
        return jsonify(purchases_list), 200
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"Error": "Request must be in JSON"}), 400
        if "product_id" not in data or "quantity" not in data:
            return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
        elif not is_int(data["product_id"]):
            return jsonify({"error":"product_id must be an int"}), 400
        if not is_number(data["quantity"]):
            return jsonify({"error":"Quantity Must be a number"}), 400
        else:
            purchase = {
                "product_id": int(data["product_id"]),
                "quantity": float(data["quantity"]),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            purchases_list.append(purchase)
            return jsonify(purchase), 201
    else:
        return jsonify({"error": "Method not allowed"}), 405

if __name__ == "__main__":
    app.run(debug=True)

#create and test on postman routes
#sales - table
#purchases - table

#create a github repo called flask api and push this code to the repo
#rest api http rules
#1. have a route
#2.always return data as json
#3.specify the request method e.g GET, POST, PUT, DELETE
#4.return status code e.g 200, 201, 400, 404, 500

#JWT is JSON Web Token - Generatednin the API and sent to the client
# A  Client(web,mobile) can not access a protected route without a token
# The client stores that toejn once they login or register
# pip install flask-jwt-extended
#Install slack + sentry integration
#Create a sentry account and a project
#Integrate sentry with flask    