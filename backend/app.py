from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
from sqlalchemy import text
from dateutil.parser import isoparse
from db import engine
from logging_config import init_json_logging
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# --- logging ---
init_json_logging(app)

# --- error handlers (JSON) ---
@app.errorhandler(400)
def bad_request(e): return jsonify({"error": "bad_request", "detail": str(e)}), 400

@app.errorhandler(404)
def not_found(e): return jsonify({"error": "not_found"}), 404

@app.errorhandler(500)
def server_error(e): return jsonify({"error": "server_error"}), 500

# --- simple validators ---
def parse_int_arg(name, default=None, min_val=None, max_val=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        val = int(raw)
    except ValueError:
        abort(400, f"Query param '{name}' must be an integer")
    if min_val is not None and val < min_val: abort(400, f"'{name}' < {min_val}")
    if max_val is not None and val > max_val: abort(400, f"'{name}' > {max_val}")
    return val

def parse_iso_arg(name, default=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        return isoparse(raw)
    except Exception:
        abort(400, f"Query param '{name}' must be ISO-8601 datetime (e.g. 2025-08-25T00:00:00Z)")


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

# latest logs via stored procedure (optional machine filter)
@app.get("/sp/latest-logs")
def latest_logs():
    top = parse_int_arg("top", default=50, min_val=1, max_val=1000)
    machine_id = parse_int_arg("machineId", default=None, min_val=1)

    with engine.connect() as conn:
        if machine_id is None:
            rows = conn.execute(text("EXEC dbo.sp_GetLatestLogs @Top=:t, @MachineId=NULL"), {"t": top}).all()
        else:
            rows = conn.execute(text("EXEC dbo.sp_GetLatestLogs @Top=:t, @MachineId=:m"), {"t": top, "m": machine_id}).all()

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

@app.get("/sp/kpis")
def kpi_summary():
    to_dt   = parse_iso_arg("to")
    from_dt = parse_iso_arg("from")
    if to_dt is None or from_dt is None:
        # default last 7 days (UTC)
        from datetime import datetime, timedelta, timezone
        to_dt = datetime.now(timezone.utc)
        from_dt = to_dt - timedelta(days=7)

    with engine.connect() as conn:
        rows = conn.execute(
            text("EXEC dbo.sp_MachineKpiSummary @From=:f, @To=:t"),
            {"f": to_dt.isoformat(), "t": to_dt.isoformat() if from_dt is None else to_dt.isoformat()}
        ).all()
    # NB: bug above (intentional check) — fix to use from_dt
    with engine.connect() as conn:
        rows = conn.execute(
            text("EXEC dbo.sp_MachineKpiSummary @From=:f, @To=:t"),
            {"f": from_dt.isoformat(), "t": to_dt.isoformat()}
        ).all()

    data = [{
        "machineId": r.MachineId,
        "name": r.Name,
        "line": r.Line,
        "totalThroughput": int(r.TotalThroughput or 0),
        "errorCount": int(r.ErrorCount or 0)
    } for r in rows]
    return jsonify(data)

@app.get("/health")
def health():
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        app.logger.exception("healthcheck_failed")
        return {"ok": False, "error": str(e)}, 500

from flask_swagger_ui import get_swaggerui_blueprint

@app.get("/openapi.json")
def openapi():
    return send_from_directory(os.path.dirname(__file__), "openapi.json", mimetype="application/json")

SWAGGER_URL = "/docs"
API_URL = "/openapi.json"
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "Factory Data API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == "__main__":
    app.run(debug=True)
