import { getToken } from "../lib/auth";

export default function DownloadReportButton() {
  const onClick = async () => {
    const token = getToken();
    if (!token) { alert("Please login as Admin to download."); return; }

    const url = `${import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000"}/reports/latest`;
    const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!r.ok) { alert("Download failed"); return; }
    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "kpi_report.xlsx";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <button onClick={onClick} style={{ padding: "6px 10px", borderRadius: 8, width: "auto" }}>
      Download KPI Report (.xlsx)
    </button>
  );
}
