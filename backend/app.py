from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text
from db import engine

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

@app.get("/machines")
def get_machines():
    sql = text("SELECT Id, Name, Status, Line FROM dbo.Machines ORDER BY Id;")
    with engine.connect() as conn:
        rows = conn.execute(sql).all()
        machines = [{"id": r.Id, "name": r.Name, "status": r.Status, "line": r.Line} for r in rows]
    return jsonify(machines)

@app.get("/logs/<int:machine_id>")
def get_logs(machine_id: int):
    sql = text("""
        SELECT Id, Ts, Type, Code, Message
        FROM dbo.Events
        WHERE MachineId = :mid
        ORDER BY Ts DESC;
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"mid": machine_id}).all()
        logs = [{
            "id": r.Id,
            "timestamp": r.Ts.isoformat() if hasattr(r.Ts, "isoformat") else str(r.Ts),
            "type": r.Type,
            "code": r.Code,
            "message": r.Message
        } for r in rows]
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)
