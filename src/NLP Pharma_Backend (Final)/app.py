from flask import Flask, request, jsonify
from config.db_config import get_connection
from flask_cors import CORS
from auth.routes import auth_bp
import random
import string
import secrets

app = Flask(__name__)

# print(secrets.token_hex(16))
app.secret_key = "89e81fb12e3428a202121a1ae1cd5b62"
# Optional for session sharing across origins
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True
CORS(app, supports_credentials=True)  # 🟢 Allow credentials

# Registering routes
app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/", methods=["GET"])
def home():
    return "💊 NLP Pharma Bot Backend is Running!"

# ----------------- WEBHOOK for Dialogflow -----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req['queryResult']['intent']['displayName']

    # Calling
    if intent == "Order_Tracking":
        return handle_order_tracking(req)
    if intent == "New_Order_Quantity":
        return handle_order(req)
    elif intent == "After_Feedback":
        return handle_feedback(req)
    elif intent == "Order_Cancel":
        return handle_cancel_order(req)
    else:
        return jsonify({"fulfillmentText": "❗ Sorry, I didn't understand that request."})

def generate_order_id():
    return 'ORD' + ''.join(random.choices(string.digits, k=6))

# Order Placements 

def handle_order(req):
    params = req['queryResult']['parameters']
    medicine_list = params.get("medicine_name", [])
    medicine = medicine_list[0] if isinstance(medicine_list, list) and medicine_list else str(medicine_list)
    quantity_raw = params.get("quantity", 0)
    quantity = int(float(quantity_raw))  
    location_list = params.get("Delivery_Location", [])
    location = location_list[0] if isinstance(location_list, list) and location_list else str(location_list)
    email_list = params.get("email", [])
    email = email_list[0] if isinstance(email_list, list) and email_list else str(email_list)
    
    order_id = generate_order_id()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Fetch price from medicines table
        cursor.execute("SELECT price FROM medicines WHERE medicine_name = %s", (medicine,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"fulfillmentText": f"❌ Medicine '{medicine}' not found in the database."})

        price_per_unit = float(result[0])
        total_price = round(price_per_unit * quantity, 2)

        # 2. Insert order into orders table
        cursor.execute(
    "INSERT INTO orders (order_id, medicine_name, quantity, location, user_email, status) VALUES (%s, %s, %s, %s, %s, %s)",
    (order_id, medicine, quantity, location, email, 'Pending')
)
        conn.commit()

        return jsonify({
            "fulfillmentText": (
                f"✅ Order placed!.\n"
                f"🆔 Order ID: {order_id}.\n"
                f"📦 {quantity} x {medicine} @ ${price_per_unit:.2f} each.\n"
                f"💰 Total: ${total_price:.2f}.\n"
                f"🚚 Delivery to: {location} in 2–3 business days. Do you need anything else?"
            )
        })

    except Exception as e:
        return jsonify({"fulfillmentText": f"❌ Failed to place order: {str(e)}"})

# Order feedback

def handle_feedback(req):
    params = req['queryResult']['parameters']
    rating_list = params.get("Feedback", [])
    rating = rating_list[0] if isinstance(rating_list, list) and rating_list else str(rating_list)
    emai_list = params.get("email", [])
    email = emai_list[0] if isinstance(emai_list, list) and emai_list else str(emai_list)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (rating, user_email) VALUES (%s, %s)", (rating, email))
        conn.commit()
        return jsonify({"fulfillmentText": "Thank you for your valuable time."})
    except Exception as e:
        return jsonify({"fulfillmentText": f"❌ Failed to save feedback: {str(e)}"})

# Order Cancellation

def handle_cancel_order(req):
    params = req['queryResult']['parameters']
    order_list = params.get("order_id", [])
    order_id = order_list[0] if isinstance(order_list, list) and order_list else str(order_list)

    if not order_id:
        return jsonify({"fulfillmentText": "❗ Please provide a valid Order ID to cancel your order."})

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Optional: Check if the order exists
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({"fulfillmentText": "❌ No order found with the provided Order ID."})

        # Cancel the order (you can either delete or update its status)
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()

        return jsonify({"fulfillmentText": f"🗑️ Order ID: {order_id} has been successfully cancelled."})

    except Exception as e:
        return jsonify({"fulfillmentText": f"❌ Failed to cancel order: {str(e)}"})

# Order Tracking 

def handle_order_tracking(req):
    parameters = req['queryResult']['parameters']
    order_id = parameters.get("order_id", "N/A")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if result:
            status = result['status']
            return jsonify({
                "fulfillmentText": f"🆔 Order ID: {order_id}\n📦 Status: {status}. \n🚚 Your order is being processed and will be dispatched soon."
            })
    except Exception as e:
        return jsonify({"fulfillmentText": f"❌ No order found with that ID. {str(e)}"})



if __name__ == "__main__":
    app.run(debug=True, port=5000)
