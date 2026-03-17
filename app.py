from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import yfinance as yf
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# 🔐 JWT Config
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- STOCK NAMES ----------------
stock_names = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "GOOGL": "Google"
}

# ---------------- ML MODEL ----------------
def get_prediction(stock):
    data = yf.download(stock, start="2022-01-01", end="2024-01-01")

    for i in range(1, 6):
        data[f'lag_{i}'] = data['Close'].shift(i)

    data['Target'] = (data['Close'] > data['Close'].shift(1)).astype(int)
    data.dropna(inplace=True)

    X = data[[f'lag_{i}' for i in range(1, 6)]]
    y = data['Target']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(X_scaled)

    split = int(len(X_pca) * 0.8)
    X_train, X_test = X_pca[:split], X_pca[split:]
    y_train, y_test = y[:split], y[split:]

    model = KNeighborsClassifier(n_neighbors=5, weights='distance')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

    latest = X.iloc[-1:].values
    latest_scaled = scaler.transform(latest)
    latest_pca = pca.transform(latest_scaled)

    prediction = model.predict(latest_pca)[0]
    result = "UP 📈" if prediction == 1 else "DOWN 📉"

    return result, accuracy

# ---------------- AUTH APIs ----------------

# 🟢 REGISTER
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"})
    except:
        return jsonify({"error": "User already exists"}), 400

# 🟢 LOGIN → RETURNS JWT TOKEN
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        token = create_access_token(identity=username)
        return jsonify({"access_token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# 🟢 PROTECTED PREDICTION API
@app.route('/api/predict', methods=['POST'])
@jwt_required()
def predict():
    current_user = get_jwt_identity()

    data = request.json
    stock = data['stock']

    prediction, accuracy = get_prediction(stock)

    return jsonify({
        "user": current_user,
        "stock": stock_names[stock],
        "prediction": prediction,
        "accuracy": accuracy
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)