from flask import Flask, jsonify, request

app = Flask(__name__)

products_list = []
sales_list = []
purchases_list = []

@app.route("/",methods=['GET'])
def home():
    res = {"flask api version": "1.0.0"}
    return jsonify(res), 200

@app.route('/api/products', methods=['GET', 'POST'])
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
def purchases():
    if request.method == "GET":
        return jsonify(purchases_list), 200
    
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"Error": "Request must be in JSON"}), 400
            if "product_id" not in data or "quantity" not in data:
                return jsonify({"error": "Ensure all fields are set: product_id, quantity"}), 400
            elif is_int(data[product_id]):
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
app.run()

#create and test on postman routes
#sales - table
#purchases - table

#create a github repo and push this code to the repo
#rest api http rules
#1. have a route
#2.always return data as json
#3.specify the request method e.g GET, POST, PUT, DELETE
#4.return status code e.g 200, 201, 400, 404, 500