import os, io
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy import text
from db import engine

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_kpi_report(from_dt=None, to_dt=None):
    # default last 7 days UTC
    if to_dt is None:
        to_dt = datetime.now(timezone.utc)
    if from_dt is None:
        from_dt = to_dt - timedelta(days=7)

    with engine.connect() as conn:
        # KPIs (via proc)
        kpi_rows = conn.execute(
            text("EXEC dbo.sp_MachineKpiSummary @From=:f, @To=:t"),
            {"f": from_dt.isoformat(), "t": to_dt.isoformat()}
        ).all()
        kpis = pd.DataFrame([{
            "MachineId": r.MachineId,
            "Name": r.Name,
            "Line": r.Line,
            "TotalThroughput": int(r.TotalThroughput or 0),
            "ErrorCount": int(r.ErrorCount or 0),
        } for r in kpi_rows])

        # Recent errors (via proc)
        err_rows = conn.execute(text("EXEC dbo.sp_GetLatestLogs @Top=:t, @MachineId=NULL"), {"t": 500}).all()
        errors = pd.DataFrame([{
            "Ts": r.Ts, "MachineId": r.MachineId, "MachineName": r.MachineName,
            "Type": r.Type, "Code": r.Code, "Message": r.Message
        } for r in err_rows if str(r.Type).upper() == "ERROR"])

        # Throughput series (hourly)
        series_rows = conn.execute(text("""
            SELECT DATETRUNC(hour, Ts) AS BucketTs, SUM(Throughput) AS TotalThroughput
            FROM dbo.Telemetry
            WHERE Ts BETWEEN :f AND :t
            GROUP BY DATETRUNC(hour, Ts)
            ORDER BY BucketTs
        """), {"f": from_dt.isoformat(), "t": to_dt.isoformat()}).all()
        series = pd.DataFrame([{"Ts": r.BucketTs, "Throughput": int(r.TotalThroughput or 0)} for r in series_rows])

    # Build workbook in memory, then save
    ts = to_dt.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"kpi_report_{ts}.xlsx")

    with pd.ExcelWriter(path, engine="xlsxwriter", datetime_format="yyyy-mm-dd hh:mm:ss") as xw:
        if not kpis.empty:   kpis.to_excel(xw, index=False, sheet_name="KPI Summary")
        if not series.empty: series.to_excel(xw, index=False, sheet_name="Throughput (hourly)")
        if not errors.empty: errors.to_excel(xw, index=False, sheet_name="Recent Errors")

        # Simple formatting
        for sheet in xw.book.worksheets():
            sheet.autofilter(0, 0, sheet.dim_rowmax, sheet.dim_colmax)
            sheet.set_column(0, sheet.dim_colmax, 20)

        # Add a quick chart (optional)
        if not series.empty:
            chart = xw.book.add_chart({"type": "line"})
            chart.add_series({
                "name": "Throughput",
                "categories": ["Throughput (hourly)", 1, 0, len(series), 0],
                "values":     ["Throughput (hourly)", 1, 1, len(series), 1],
            })
            chart.set_title({"name": "Throughput Over Time"})
            xw.book.get_worksheet_by_name("Throughput (hourly)").insert_chart("D2", chart, {"x_scale": 1.2, "y_scale": 1.2})

    return path
