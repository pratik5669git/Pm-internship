from flask import Flask, request, jsonify
import pandas as pd
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ enable CORS for all routes

USER_FILE = "users.csv"
STUDENT_FILE = "students.csv"

# ✅ Ensure CSV exists with headers
if not os.path.exists(USER_FILE):
    df = pd.DataFrame(columns=["email", "password", "role", "company_id"])
    df.to_csv(USER_FILE, index=False)

# ✅ Ensure student CSV exists with headers
if not os.path.exists(STUDENT_FILE):
    with open(STUDENT_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "phone", "role"])
        writer.writeheader()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    company_id = data.get("company_id", "")

    df = pd.read_csv(USER_FILE)

    # check if email already exists
    if email in df["email"].values:
        return jsonify({"success": False, "message": "User already exists!"})

    # add new user
    new_user = pd.DataFrame([{
        "email": email,
        "password": password,
        "role": role,
        "company_id": company_id if role == "company" else ""
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

    return jsonify({"success": True, "message": "Signup successful!"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    login_type = data.get("login_type")
    company_id = data.get("company_id", "")

    df = pd.read_csv(USER_FILE)

    # check credentials
    user = df[(df["email"] == email) &
              (df["password"] == password) &
              (df["role"] == login_type)]

    if login_type == "company":
        user = user[user["company_id"] == company_id]

    if not user.empty:
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials!"})


@app.route("/register_student", methods=["POST"])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid data"}), 400

    # Read existing data to check for duplicates
    existing_emails = set()
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_emails.add(row["email"])
    
    # Check if email already exists
    if data.get("email") in existing_emails:
        return jsonify({"success": False, "message": "Student with this email already registered!"}), 400

    # Append new student data
    with open(STUDENT_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "phone", "role"])
        writer.writerow(data)

    return jsonify({"success": True, "message": "Student registered successfully"})


if __name__ == "__main__":
    app.run(debug=True)