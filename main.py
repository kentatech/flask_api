from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
# import sentry_sdk
from flask_cors import CORS
from models import db, Product, Sale, Purchase, User
from configs.base_configs import Development
from dotenv import load_dotenv 

#load env variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up configurations
app_config = Development()
app.config.from_object(app_config)

# Initialize Sentry for error tracking
# sentry_sdk.init(
#     dsn=app.config.get('SENTRY_DSN')
# )

# Initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NEWPAS4u.@localhost:5432/flask_api'
db.init_app(app)

# Configure JWT
jwt = JWTManager(app)

# Helper functions
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
     res = {"flask api version": "2.0.0"}
     return jsonify(res), 200

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if "username" not in data.keys() or "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
    elif User.query.filter_by(email=data["email"]).first() is not None:
        error = {"error": "User with that email already exists"}
        return jsonify(error), 409
        #Elif expected to check mail is valid/exists
    else:
        usrs = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(usrs)
        db.session.commit()
        data["id"] = usrs.id
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
        usr = User.query.filter_by(email=data["email"], password=data["password"]).first() 
        if usr is None:
            error = {"error": "Invalid email or password"}
            return jsonify(error), 401
        else:
            token = create_access_token(identity = data["email"])
            return jsonify({"token": token}), 200  

@app.route("/api/users")
def get_users():
    if request.method == "GET":
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405

@app.route('/api/products', methods=['GET', 'POST'])
@jwt_required()
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([prod.to_dict() for prod in products]), 200
    elif request.method == 'POST':
        data =request.get_json()
        if 'name' not in data or 'buying_price' not in data.keys() or 'selling_price' not in data.keys():
            error = {"error" : "ensure all fields are filled"}
            return jsonify(error), 400
        else:
           # products_list.append(data) replaced with the below three-four lines
           prod = Product(name=data['name'], buying_price=data['buying_price'], selling_price=data['selling_price'])
           db.session.add(prod)
           db.session.commit()
           data["id"] = prod.id
           return jsonify(data),201
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405
    
@app.route("/api/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    if request.method == "GET":
        sales = Sale.query.all()
        return jsonify([sale.to_dict() for sale in sales]), 200
    elif request.method == "POST":
        data_s = request.get_json()
        if not data_s:
            return jsonify({"error": "Request must be in json"}), 400
        if "product_id" not in data_s or "quantity" not in data_s:
            return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
        elif not is_int(data_s["product_id"]):
            return jsonify({"error": "product_id must be an int"}), 400
        elif not is_number(data_s["quantity"]):
            return jsonify({"error": "quantity must be a number"}), 400
        s = Sale(product_id=int(data_s["product_id"]), quantity=float(data_s["quantity"]))
        db.session.add(s)
        db.session.commit()
        data_s["id"] = s.id
        data_s["created_at"] = s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        # sales_list.append(sale) # commented out replaced by abovve five lines
        return jsonify(data_s), 201
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405
        
@app.route("/api/purchases", methods=["GET", "POST"])
@jwt_required()
def purchases():
    if request.method == "GET":
        purchases = Purchase.query.all()
        return jsonify([purch.to_dict() for purch in purchases]), 200
    elif request.method == "POST":
        data_p = request.get_json()
        if not data_p:
            return jsonify({"Error": "Request must be in JSON"}), 400
        if "product_id" not in data_p or "quantity" not in data_p:
            return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
        elif not is_int(data_p["product_id"]):
            return jsonify({"error":"product_id must be an int"}), 400
        elif not is_number(data_p["quantity"]):
            return jsonify({"error":"Quantity Must be a number"}), 400
        
        purch = Purchase(product_id=int(data_p["product_id"]), quantity=float(data_p["quantity"]))
        db.session.add(purch)
        db.session.commit()
        data_p["id"] = purch.id
        data_p["created_at"] = purch.created_at.strftime("%Y-%m-%d %H:%M:%S")
        # purchases_list.append(purchase) # commented out replaced by above five lines
    
        return jsonify(data_p), 201
    else:
        return jsonify({"error": "Method not allowed"}), 405

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
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
# add unit tests in a file called mytests.py   