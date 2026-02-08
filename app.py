from flask import Flask, request, jsonify
import sqlite3
import math

app = Flask(__name__)

# ---------------- Database Setup ----------------
conn = sqlite3.connect('village_health.db', check_same_thread=False)
cursor = conn.cursor()

# Volunteers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    latitude REAL,
    longitude REAL
)
""")

# Patients table
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    latitude REAL,
    longitude REAL
)
""")

# Pharmacies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pharmacies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    latitude REAL,
    longitude REAL,
    medicine_name TEXT,
    quantity INTEGER
)
""")

# Requests table
cursor.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    volunteer_id INTEGER,
    pharmacy_id INTEGER,
    medicine_name TEXT,
    quantity INTEGER,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Usage logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ---------------- Helper Function ----------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------- APIs ----------------

@app.route('/add_volunteer', methods=['POST'])
def add_volunteer():
    data = request.get_json()
    cursor.execute("INSERT INTO volunteers (name, latitude, longitude) VALUES (?, ?, ?)",
                   (data['name'], data['latitude'], data['longitude']))
    conn.commit()
    return jsonify({"message": "Volunteer added"})

@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.get_json()
    cursor.execute("INSERT INTO patients (name, latitude, longitude) VALUES (?, ?, ?)",
                   (data['name'], data['latitude'], data['longitude']))
    conn.commit()
    return jsonify({"message": "Patient added"})

@app.route('/add_pharmacy', methods=['POST'])
def add_pharmacy():
    data = request.get_json()
    cursor.execute("""INSERT INTO pharmacies (name, latitude, longitude, medicine_name, quantity)
                      VALUES (?, ?, ?, ?, ?)""",
                   (data['name'], data['latitude'], data['longitude'], data['medicine_name'], data['quantity']))
    conn.commit()
    return jsonify({"message": "Pharmacy added"})

@app.route('/request_volunteer', methods=['POST'])
def request_volunteer():
    data = request.get_json()
    lat, lon = data['latitude'], data['longitude']
    cursor.execute("SELECT id, name, latitude, longitude FROM volunteers")
    vols = cursor.fetchall()
    if not vols:
        return jsonify({"message": "No volunteers available"})
    nearest = min(vols, key=lambda v: calculate_distance(lat, lon, v[2], v[3]))
    dist = round(calculate_distance(lat, lon, nearest[2], nearest[3]), 2)
    return jsonify({"volunteer_id": nearest[0], "name": nearest[1], "distance_km": dist})

@app.route('/assign_volunteer', methods=['POST'])
def assign_volunteer():
    data = request.get_json()
    cursor.execute("""INSERT INTO requests (patient_id, volunteer_id, status)
                      VALUES (?, ?, ?)""",
                   (data['patient_id'], data['volunteer_id'], "assigned"))
    cursor.execute("INSERT INTO usage_logs (action) VALUES (?)", ("Volunteer assigned",))
    conn.commit()
    return jsonify({"message": "Volunteer assigned successfully"})

@app.route('/request_medicine', methods=['POST'])
def request_medicine():
    data = request.get_json()
    med = data['medicine_name']
    qty = data['quantity']
    lat, lon = data['latitude'], data['longitude']
    cursor.execute("SELECT id, name, latitude, longitude, quantity FROM pharmacies WHERE medicine_name=?", (med,))
    phs = cursor.fetchall()
    available = [p for p in phs if p[4] >= qty]
    if not available:
        return jsonify({"message": "Not enough stock"})
    nearest = min(available, key=lambda p: calculate_distance(lat, lon, p[2], p[3]))
    return jsonify({"pharmacy_id": nearest[0], "name": nearest[1]})

@app.route('/confirm_medicine_order', methods=['POST'])
def confirm_medicine_order():
    data = request.get_json()
    pharmacy_id = data['pharmacy_id']
    qty = data['quantity']
    cursor.execute("SELECT quantity FROM pharmacies WHERE id=?", (pharmacy_id,))
    current = cursor.fetchone()[0]
    if current < qty:
        return jsonify({"message": "Not enough stock"})
    cursor.execute("UPDATE pharmacies SET quantity=? WHERE id=?", (current - qty, pharmacy_id))
    cursor.execute("INSERT INTO usage_logs (action) VALUES (?)", ("Medicine order confirmed",))
    conn.commit()
    return jsonify({"message": "Medicine order confirmed, stock updated"})

@app.route('/view_logs', methods=['GET'])
def view_logs():
    cursor.execute("SELECT * FROM usage_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    return jsonify(logs)

@app.route('/doctor_login', methods=['POST'])
def doctor_login():
    data = request.get_json()
    if data['username'] == "doctor" and data['password'] == "1234":
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True)
