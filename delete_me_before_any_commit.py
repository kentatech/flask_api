
# Route to handle both GET and POST requests
@app.route('/api/payments/mpesa', methods=['GET', 'POST'])
def handle_mpesa_payment():
    # Handle GET request first
    if request.method == 'GET':
        # Fetch all payment records from the database
        payments = Payment.query.all()

        # If records exist, return them
        if payments:
            return jsonify([payment.to_dict() for payment in payments]), 200
        else:
            return jsonify({"message": "No payments found"}), 404

    # Handle POST request to receive M-Pesa data
    elif request.method == 'POST':
        # Simulate fetching data from M-Pesa API
        mpesa_api_url = "https://api.safaricom.co.ke/mpesa/transaction"  # placeholder
        response = requests.get(mpesa_api_url)

        # Check if the API call was successful
        if response.status_code == 200:
            data = response.json()

            # Check if required fields are present
            if "sale_id" in data and "trans_amount" in data and "trans_name" in data:
                model = data["model"] if "model" in data else "mpesa"
                sale_id = data["sale_id"]
                mpesa_ref = data["mpesa_ref"] if "mpesa_ref" in data else None
                trans_amount = data["trans_amount"]
                trans_name = data["trans_name"]

                # Create and save the payment
                new_payment = Payment(
                    model=model,
                    sale_id=sale_id,
                    mpesa_ref=mpesa_ref,
                    trans_amount=trans_amount,
                    trans_name=trans_name
                )
                db.session.add(new_payment)
                try:
                    db.session.commit()
                    return jsonify({
                        "message": "Payment recorded successfully",
                        "payment": new_payment.to_dict()
                    }), 201
                except:
                    db.session.rollback()
                    return jsonify({"error": "Database commit failed"}), 500
            else:
                return jsonify({"error": "Missing required fields"}), 400
        else:
            return jsonify({"error": "Failed to fetch M-Pesa data"}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)