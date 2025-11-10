from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from sqlalchemy import func
from models import db, Product, Sale, Purchase, User , SalesDetails
from configs.base_configs import Development
from dotenv import load_dotenv 
# import sentry_sdk

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

#dashboard route to display sales count - front end will use chart j.s to display sales count
@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if request.method == "GET":
       # Calculate remaining stock per product
        remaining_stock_query = (
            db.session.query(
                Product.id,
                Product.name,
                (
                    func.coalesce(func.sum(Purchase.quantity), 0)
                    - func.coalesce(func.sum(SalesDetails.quantity), 0)
                ).label("remaining_stock")
            )
            .outerjoin(Purchase, Product.id == Purchase.product_id)
            .outerjoin(SalesDetails, Product.id == SalesDetails.product_id)
            .group_by(Product.id, Product.name)
        )
        results = remaining_stock_query.all()
        # print('------------------------------------------------------------------',results)
        data = []
        labels = []
        for r in results:
            data.append(r.remaining_stock)
            labels.append(r.name)
        return jsonify({"data":data, "labels":labels}), 200
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405

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
    # add logic to get if get fails redirect user to login

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
        sales = Sale.query.order_by(Sale.created_at.desc()).all()
        result = []

        for sale in sales:
            details = (
                db.session.query(SalesDetails, Product)
                .join(Product, Product.id == SalesDetails.product_id)
                .filter(SalesDetails.sale_id == sale.id)
                .all()
            )

            sale_dict = {
                "sale_id": sale.id,
                "created_at": sale.created_at.strftime("%Y-%m-%d %H:%M"),
                "items": []
            }

            for detail, product in details:
                sale_dict["items"].append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": detail.quantity
                })

            result.append(sale_dict)

        return jsonify(result), 200

    elif request.method == "POST":
        data = request.get_json()

        # --- Handle bulk sales: { "items": [ { "product_id": 1, "quantity": 2 }, ... ] } ---
        if "items" in data and isinstance(data["items"], list):
            items = data["items"]
            if not items:
                return jsonify({"error": "No sale items provided"}), 400

            try:
                new_sale = Sale()
                db.session.add(new_sale)
                db.session.flush()  # get new_sale.id

                responses = []

                for item in items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity")

                    if not is_int(product_id) or not is_number(quantity):
                        return jsonify({"error": "product_id must be int and quantity must be number"}), 400

                    product_id = int(product_id)
                    quantity = float(quantity)

                    # --- Stock check ---
                    total_purchased = db.session.query(func.sum(Purchase.quantity)).filter_by(product_id=product_id).scalar() or 0
                    total_sold = db.session.query(func.sum(SalesDetails.quantity)).filter_by(product_id=product_id).scalar() or 0
                    available_stock = total_purchased - total_sold

                    if available_stock <= 0:
                        return jsonify({"error": f"No stock available for product {product_id}"}), 400
                    if quantity > available_stock:
                        return jsonify({"error": f"Only {available_stock} items left for product {product_id}"}), 400

                    # --- Create sale detail ---
                    sale_detail = SalesDetails(
                        sale_id=new_sale.id,
                        product_id=product_id,
                        quantity=quantity
                    )
                    db.session.add(sale_detail)

                    responses.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "available_stock": available_stock
                    })

                db.session.commit()

                return jsonify({
                    "message": f"{len(items)} sales recorded successfully!",
                    "sale_id": new_sale.id,
                    "items": responses
                }), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

        # --- Handle single sale: { "product_id": 1, "quantity": 2 } ---
        elif "product_id" in data and "quantity" in data:
            if not is_int(data["product_id"]):
                return jsonify({"error": "product_id must be an int"}), 400
            if not is_number(data["quantity"]):
                return jsonify({"error": "quantity must be a number"}), 400

            product_id = int(data["product_id"])
            quantity = float(data["quantity"])

            total_purchased = db.session.query(func.sum(Purchase.quantity)).filter_by(product_id=product_id).scalar() or 0
            total_sold = db.session.query(func.sum(SalesDetails.quantity)).filter_by(product_id=product_id).scalar() or 0
            available_stock = total_purchased - total_sold

            if available_stock <= 0:
                return jsonify({"error": "No stock available"}), 400
            if quantity > available_stock:
                return jsonify({"error": f"Only {available_stock} items left"}), 400

            try:
                new_sale = Sale()
                db.session.add(new_sale)
                db.session.flush()

                sale_detail = SalesDetails(
                    sale_id=new_sale.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(sale_detail)
                db.session.commit()

                return jsonify({
                    "id": new_sale.id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "created_at": new_sale.created_at.strftime("%Y-%m-%d %H:%M"),
                    "available_stock": available_stock
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

        else:
            return jsonify({"error": "Invalid request format"}), 400
    
# @app.route("/api/sales", methods=["GET", "POST"])
# @jwt_required()
# def sales():
#     if request.method == "GET":
#         sales = Sale.query.order_by(Sale.created_at.desc()).all()
#         result = []

#         for sale in sales:
#             details = (
#                 db.session.query(SalesDetails, Product)
#                 .join(Product, Product.id == SalesDetails.product_id)
#                 .filter(SalesDetails.sale_id == sale.id)
#                 .all()
#             )

#             sale_dict = {
#                 "sale_id": sale.id,
#                 "created_at": sale.created_at.strftime("%Y-%m-%d %H:%M"),
#                 "items": []
#             }

#             for detail, product in details:
#                 sale_dict["items"].append({
#                     "product_id": product.id,
#                     "product_name": product.name,
#                     "quantity": detail.quantity
#                 })
#             # print("-------------------------------------------------------------------",sale_dict)
#             result.append(sale_dict)

#         return jsonify(result), 200

#     elif request.method == "POST":
#         data = request.get_json()

#         # Handle bulk sale: { "items": [ { "product_id": 1, "quantity": 2 }, ... ] }
#         if "items" in data and isinstance(data["items"], list):
#             items = data["items"]
#             if not items:
#                 return jsonify({"error": "No sale items provided"}), 400

#             try:
#                 new_sale = Sale()
#                 db.session.add(new_sale)
#                 db.session.flush()  # get new_sale.id

#                 for item in items:
#                     product_id = item.get("product_id")
#                     quantity = item.get("quantity")

#                     if not is_int(product_id) or not is_number(quantity):
#                         return jsonify({"error": "product_id must be int and quantity must be number"}), 400

#                     product_id = int(product_id)
#                     quantity = float(quantity)

#                     # Stock availability check
#                     total_purchased = db.session.query(func.sum(Purchase.quantity)).filter_by(product_id=product_id).scalar() or 0
#                     total_sold = db.session.query(func.sum(SalesDetails.quantity)).filter_by(product_id=product_id).scalar() or 0
#                     available_stock = total_purchased - total_sold

#                     if available_stock <= 0:
#                         return jsonify({"error": f"No stock available for product {product_id}"}), 400
#                     if quantity > available_stock:
#                         return jsonify({"error": f"Only {available_stock} items left for product {product_id}"}), 400

#                     # Add sale detail
#                     sale_detail = SalesDetails(
#                         sale_id=new_sale.id,
#                         product_id=product_id,
#                         quantity=quantity
#                     )
#                     db.session.add(sale_detail)

#                     db.session.commit()
#                     return jsonify({"message": "Sales recorded successfully!", "sale_id": new_sale.id, "available_stock":available_stock}), 201

#             except Exception as e:
#                 db.session.rollback()
#                 return jsonify({"error": str(e)}), 500

#         # Handle single sale: { "product_id": 1, "quantity": 2 }
#         elif "product_id" in data and "quantity" in data:
#             if not is_int(data["product_id"]):
#                 return jsonify({"error": "product_id must be an int"}), 400
#             if not is_number(data["quantity"]):
#                 return jsonify({"error": "quantity must be a number"}), 400

#             product_id = int(data["product_id"])
#             quantity = float(data["quantity"])

#             # Stock validation
#             total_purchased = db.session.query(func.sum(Purchase.quantity)).filter_by(product_id=product_id).scalar() or 0
#             total_sold = db.session.query(func.sum(SalesDetails.quantity)).filter_by(product_id=product_id).scalar() or 0
#             available_stock = total_purchased - total_sold

#             if available_stock <= 0:
#                 return jsonify({"error": "No stock available"}), 400
#             if quantity > available_stock:
#                 return jsonify({"error": f"Only {available_stock} items left"}), 400

#             # Record single sale
#             try:
#                 new_sale = Sale()
#                 db.session.add(new_sale)
#                 db.session.flush()

#                 sale_detail = SalesDetails(
#                     sale_id=new_sale.id,
#                     product_id=product_id,
#                     quantity=quantity
#                 )
#                 db.session.add(sale_detail)
#                 db.session.commit()

#                 return jsonify({
#                     "id": new_sale.id,
#                     "product_id": product_id,
#                     "quantity": quantity,
#                     "created_at": new_sale.created_at.strftime("%Y-%m-%d %H:%M"),
#                     "available_stock": available_stock
#                 }), 201
#             except Exception as e:
#                 db.session.rollback()
#                 return jsonify({"error": str(e)}), 500

#         # Invalid request format
#         else:
#             return jsonify({"error": "Invalid request format"}), 400
        # data_s = request.get_json()
        # if not data_s:
        #     return jsonify({"error": "Request must be in json"}), 400
        # if "product_id" not in data_s or "quantity" not in data_s:
        #     return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
        # elif not is_int(data_s["product_id"]):
        #     return jsonify({"error": "product_id must be an int"}), 400
        # elif not is_number(data_s["quantity"]):
        #     return jsonify({"error": "quantity must be a number"}), 400
        
        # #  calculate stock availability
        # product_id = data_s.get("product_id")
        # quantity = float(data_s.get("quantity", 0))
        # # Calculate current stock = purchases - sales
        # total_purchased = db.session.query(func.sum(Purchase.quantity)).filter_by(product_id=product_id).scalar() or 0
        # total_sold = db.session.query(func.sum(Sale.quantity)).filter_by(product_id=product_id).scalar() or 0
        # available_stock = total_purchased - total_sold
        # if available_stock <= 0:
        #     return jsonify({"error": "No stock available"}), 400
        # if quantity > available_stock:
        #     return jsonify({"error": f"Only {available_stock} items left"}), 400

        # # Create sale record
        # #instruct how to create sale record
        # s = Sale(product_id=int(data_s["product_id"]), quantity=float(data_s["quantity"]))
        # db.session.add(s)
        # db.session.commit()
        # data_s["id"] = s.id
        # data_s["created_at"] = s.created_at.strftime("%Y-%m-%d %H:%M")
        # # sales_list.append(sale) # commented out replaced by abovve five lines
        # return jsonify(data_s), 201
    # else:
    #     error = {"error": "Method not allowed"}
    #     return jsonify(error), 405
# @app.route("/api/stock", methods=["GET"])
# @jwt_required()
# def stock():
#     products = Product.query.all()
#     stock_data = []

#     for product in products:
#         # calculate available stock exactly like in your sales route
#         total_purchased = (
#             db.session.query(func.sum(Purchase.quantity))
#             .filter_by(product_id=product.id)
#             .scalar()
#             or 0
#         )
#         total_sold = (
#             db.session.query(func.sum(SalesDetails.quantity))
#             .filter_by(product_id=product.id)
#             .scalar()
#             or 0
#         )

#         available_stock = total_purchased - total_sold

#         stock_data.append({
#             "product_id": product.id,
#             "name": product.name,
#             "available_quantity": available_stock
#         })

#     return jsonify(stock_data), 200

        
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
        data_p["created_at"] = purch.created_at.strftime("%Y-%m-%d %H:%M")
        # purchases_list.append(purchase) # commented out replaced by above five lines
    
        return jsonify(data_p), 201
    else:
        return jsonify({"error": "Method not allowed"}), 405
    
@app.route("/api/stock", methods=["GET"])
def stock_summary():
     # --- Total purchased per product ---
    purchase_subq = (
        db.session.query(
            Purchase.product_id,
            func.coalesce(func.sum(Purchase.quantity), 0).label("total_purchased")
        )
        .group_by(Purchase.product_id)
        .subquery()
    )

    # --- Total sold per product (from SalesDetails now) ---
    sales_subq = (
        db.session.query(
            SalesDetails.product_id,
            func.coalesce(func.sum(SalesDetails.quantity), 0).label("total_sold")
        )
        .group_by(SalesDetails.product_id)
        .subquery()
    )

    # --- Join with products to get names ---
    query = (
        db.session.query(
            Product.id.label("product_id"),
            Product.name,
            (
                func.coalesce(purchase_subq.c.total_purchased, 0)
                - func.coalesce(sales_subq.c.total_sold, 0)
            ).label("available_quantity")
        )
        .outerjoin(purchase_subq, Product.id == purchase_subq.c.product_id)
        .outerjoin(sales_subq, Product.id == sales_subq.c.product_id)
        .order_by(Product.name)
    )

    results = query.all()

    # --- Convert to JSON-friendly list ---
    stock = [
        {
            "product_id": r.product_id,
            "name": r.name,
            "available_quantity": float(r.available_quantity or 0)
        }
        for r in results
    ]

    return jsonify(stock), 200

    
# build logout route that requires jwt token
@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful"}), 200


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