from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

DB_PATH = "factory.db"

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows

@app.route("/machines", methods=["GET"])
def get_machines():
    rows = query_db("SELECT * FROM machines")
    machines = [{"id": r[0], "name": r[1], "status": r[2]} for r in rows]
    return jsonify(machines)

@app.route("/logs/<int:machine_id>", methods=["GET"])
def get_logs(machine_id):
    rows = query_db("SELECT * FROM logs WHERE machine_id = ? ORDER BY timestamp DESC", (machine_id,))
    logs = [{"id": r[0], "machine_id": r[1], "timestamp": r[2], "message": r[3]} for r in rows]
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)
