from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime
import random

app = Flask(__name__)
CORS(app)

SECRET_KEY = "mysecret123"

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate_token(username):
    return jwt.encode({
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["user"]
    except:
        return None

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (data["username"], data["password"]))
        conn.commit()
        return jsonify({"message": "User registered successfully"})
    except:
        return jsonify({"error": "User already exists"}), 400
    finally:
        conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (data["username"], data["password"]))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"token": generate_token(data["username"])})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/predict", methods=["POST"])
def predict():
    auth = request.headers.get("Authorization")

    if not auth:
        return jsonify({"error": "Token missing"}), 401

    try:
        token = auth.split(" ")[1]
    except:
        return jsonify({"error": "Invalid token format"}), 401

    user = verify_token(token)

    if not user:
        return jsonify({"error": "Invalid token"}), 401

    data = request.get_json()
    stock = data.get("stock")

    if not stock:
        return jsonify({"error": "Stock required"}), 400

    stock = stock.upper()

    open_price = random.uniform(100, 300)
    close_price = random.uniform(100, 300)

    prediction = "UP 📈" if close_price > open_price else "DOWN 📉"
    accuracy = round(random.uniform(75, 95), 2)

    return jsonify({
        "user": user,
        "stock": stock,
        "prediction": prediction,
        "accuracy": accuracy
    })

if __name__ == "__main__":
    app.run(debug=True)