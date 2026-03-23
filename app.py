from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('home'))
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------- CREATE USER ----------
@app.route('/create-user')
def create_user():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username,password) VALUES (?,?)", ("admin","admin123"))
    conn.commit()
    conn.close()
    return "User created"

# ---------- PREDICTION ----------
@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    stock = data.get("stock")

    if not stock:
        return jsonify({"error": "Enter stock name"})

    # Simple logic
    open_price = random.randint(100, 300)
    close_price = random.randint(100, 300)

    prediction = "UP 📈" if close_price > open_price else "DOWN 📉"
    accuracy = round(random.uniform(70, 90), 2)

    # Graph generation
    if not os.path.exists("static"):
        os.makedirs("static")

    x = [1,2,3,4,5]
    y = [random.randint(100,200) for _ in x]

    plt.figure()
    plt.plot(x, y)
    plt.title("Stock Trend")
    plt.savefig("static/graph.png")
    plt.close()

    return jsonify({
        "prediction": prediction,
        "accuracy": accuracy
    })

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)