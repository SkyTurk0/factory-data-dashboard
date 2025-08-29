# etl/ingest_logs.py
import csv, glob, hashlib, json, os, sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text

# --- DB config from env (fallbacks for local dev) ---
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME   = os.getenv("DB_NAME")
DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASS")
ODBC_DRIVER = os.getenv("ODBC_DRIVER")

CONN_STR = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}"
    f"?driver={ODBC_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)

DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()
STATE_DIR = Path(os.getenv("STATE_DIR", ".etl_state")).resolve()
STATE_DIR.mkdir(exist_ok=True)

engine = create_engine(CONN_STR, pool_pre_ping=True, future=True)

def file_processed(fp: Path) -> bool:
    # Simple per-file fingerprint to avoid re-processing
    h = hashlib.sha256(fp.read_bytes()).hexdigest()
    state_file = STATE_DIR / (fp.name + ".sha256")
    if state_file.exists() and state_file.read_text() == h:
        return True
    state_file.write_text(h)
    return False

def get_machine_id(conn, name: str) -> int:
    row = conn.execute(
        text("SELECT Id FROM dbo.Machines WHERE Name = :n"),
        {"n": name}
    ).fetchone()
    if row:
        return int(row.Id)
    # create if not exists (optional)
    r2 = conn.execute(
        text("INSERT INTO dbo.Machines (Name, Line, Status) OUTPUT INSERTED.Id VALUES (:n, 'LineX', 'RUNNING')"),
        {"n": name}
    ).fetchone()
    return int(r2[0])

def parse_iso(ts: str) -> str:
    # Return ISO string acceptable by SQL Server (DATETIME2)
    try:
        return datetime.fromisoformat(ts.replace("Z","+00:00")).isoformat()
    except Exception:
        raise ValueError(f"Bad timestamp: {ts}")

def ingest_events(conn, fp: Path):
    print(f"[ETL] Ingesting events from {fp}")
    if file_processed(fp):
        print(f"[ETL] Skipping (already processed): {fp.name}")
        return
    with fp.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Optional: lightweight dedupe per file using a hash set
    seen = set()
    inserted = 0
    for r in rows:
        mname = r["MachineName"].strip()
        etype = r["Type"].strip().upper()
        code  = (r.get("Code") or "").strip() or None
        msg   = (r.get("Message") or "").strip() or None
        ts    = parse_iso(r["Ts"].strip())

        # content signature
        sig = hashlib.sha1(f"{mname}|{etype}|{code}|{msg}|{ts}".encode()).hexdigest()
        if sig in seen:
            continue
        seen.add(sig)

        mid = get_machine_id(conn, mname)
        conn.execute(text("""
            INSERT INTO dbo.Events (MachineId, Ts, Type, Code, Message)
            VALUES (:mid, :ts, :typ, :code, :msg)
        """), {"mid": mid, "ts": ts, "typ": etype, "code": code, "msg": msg})
        inserted += 1

    print(f"[ETL] Events inserted: {inserted}")

def ingest_telemetry(conn, fp: Path):
    print(f"[ETL] Ingesting telemetry from {fp}")
    if file_processed(fp):
        print(f"[ETL] Skipping (already processed): {fp.name}")
        return
    items = json.loads(fp.read_text(encoding="utf-8"))

    seen = set()
    inserted = 0
    for r in items:
        mname = str(r["MachineName"]).strip()
        ts    = parse_iso(str(r["Ts"]).strip())
        temp  = r.get("Temperature")
        vib   = r.get("Vibration")
        thr   = r.get("Throughput")

        sig = hashlib.sha1(f"{mname}|{ts}|{temp}|{vib}|{thr}".encode()).hexdigest()
        if sig in seen:
            continue
        seen.add(sig)

        mid = get_machine_id(conn, mname)
        conn.execute(text("""
            INSERT INTO dbo.Telemetry (MachineId, Ts, Temperature, Vibration, Throughput)
            VALUES (:mid, :ts, :t, :v, :th)
        """), {"mid": mid, "ts": ts, "t": temp, "v": vib, "th": thr})
        inserted += 1

    print(f"[ETL] Telemetry inserted: {inserted}")

def main():
    if not DATA_DIR.exists():
        print(f"[ETL] Data dir does not exist: {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    with engine.begin() as conn:
        # CSV events
        for fp in sorted(DATA_DIR.glob("events_*.csv")):
            ingest_events(conn, fp)

        # JSON telemetry
        for fp in sorted(DATA_DIR.glob("telemetry_*.json")):
            ingest_telemetry(conn, fp)

    print("[ETL] Done.")

if __name__ == "__main__":
    main()
