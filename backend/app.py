from flask import Flask, jsonify, request
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

# NEW: latest logs via stored procedure (optional machine filter)
@app.get("/sp/latest-logs")
def latest_logs():
    top = int(request.args.get("top", 50))
    machine_id = request.args.get("machineId")  # may be None
    with engine.connect() as conn:
        if machine_id is None:
            rows = conn.execute(text("EXEC dbo.sp_GetLatestLogs @Top=:t, @MachineId=NULL"), {"t": top}).all()
        else:
            rows = conn.execute(text("EXEC dbo.sp_GetLatestLogs @Top=:t, @MachineId=:m"), {"t": top, "m": int(machine_id)}).all()
    data = [{
        "id": r.Id,
        "machineId": r.MachineId,
        "timestamp": r.Ts.isoformat() if hasattr(r.Ts, "isoformat") else str(r.Ts),
        "type": r.Type,
        "code": r.Code,
        "message": r.Message,
        "machineName": r.MachineName,
        "line": r.Line,
        "severityRank": r.SeverityRank
    } for r in rows]
    return jsonify(data)

# NEW: KPI summary via stored procedure (date window)
@app.get("/sp/kpis")
def kpi_summary():
    # Defaults: last 7 days
    to_ts = request.args.get("to")
    from_ts = request.args.get("from")
    if not to_ts:
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        to_dt = now
        from_dt = now - timedelta(days=7)
        to_ts = to_dt.isoformat(timespec="seconds")
        from_ts = from_dt.isoformat(timespec="seconds")

    with engine.connect() as conn:
        rows = conn.execute(text("EXEC dbo.sp_MachineKpiSummary @From=:f, @To=:t"),
                            {"f": from_ts, "t": to_ts}).all()
    data = [{
        "machineId": r.MachineId,
        "name": r.Name,
        "line": r.Line,
        "totalThroughput": int(r.TotalThroughput or 0),
        "errorCount": int(r.ErrorCount or 0)
    } for r in rows]
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
