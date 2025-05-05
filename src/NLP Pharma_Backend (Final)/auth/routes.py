from flask import Blueprint, request, jsonify
from config.db_config import get_connection
from auth.utils import hash_password, verify_password
from auth.forget_password import generate_otp, send_otp_email, otp_storage
from flask import session

auth_bp = Blueprint("auth", __name__)
CURRENT_USER_EMAIL = None


    # ------------------- Sign Up -------------------

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    password = hash_password(data.get("password"))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

        existing_user = cursor.fetchone()

    

        if existing_user:
            return jsonify({
                "success": False,
                "message": "❌ This email is already registered. Try with another email."
            }), 409
        
        cursor.execute(
        "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)",
        (full_name, email, password, 'user')
)

        conn.commit()
        return jsonify({"message": "🟢 Signup successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Logout

@auth_bp.route("/logout", methods=["POST"])
def logout():
    global CURRENT_USER_EMAIL
    CURRENT_USER_EMAIL = None
    return jsonify({"success": True, "message": "Logged out"})

    
    # ------------------- Login -------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    global CURRENT_USER_EMAIL  # use the global variable
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and verify_password(password, user['password']):
            CURRENT_USER_EMAIL = user['email']  # ✅ set static variable
            return jsonify({
                "success": True,
                "role": user["role"],
                "message": "Login successful"
            })
        else:
            return jsonify({"success": False, "message": "🔴 Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    

    # ------------------- FORGET PASSWORD APIs -------------------

@auth_bp.route("/forget_password", methods=["POST"])
def forget_password():
    data = request.get_json()
    email = data.get("email")

    # Check if email is provided
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    # Generate OTP
    otp = generate_otp()
    otp_storage[email] = otp  # Store OTP temporarily

    # Send OTP email
    if send_otp_email(email, otp):
        return jsonify({"success": True, "message": "OTP sent successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to send OTP"}), 500

    # Verify OPT

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if otp_storage.get(email) == otp:

        return jsonify({"success": True, "message": "OTP verified"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

    # Reset Password

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = hash_password(data.get("password"))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        conn.commit()
        return jsonify({"success": True, "message": "Password updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
        # ------------------- User and Admin Dashboards -------------------

# User Dashboard – get user's own orders
@auth_bp.route("/user/orders", methods=["GET"])
def get_user_orders():
    global CURRENT_USER_EMAIL
    # if not CURRENT_USER_EMAIL:
    #     return jsonify({"success": False, "message": "Not logged in"}), 401

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE user_email = %s ORDER BY order_date DESC", ('ilsaafzaal4@gmail.com',))
        orders = cursor.fetchall()
        return jsonify({"success": True, "orders": orders})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# Admin Dashboard – get all users' orders
@auth_bp.route("/admin/orders", methods=["GET"])
def get_all_orders():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
        orders = cursor.fetchall()
        return jsonify({"success": True, "orders": orders})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


    
    




