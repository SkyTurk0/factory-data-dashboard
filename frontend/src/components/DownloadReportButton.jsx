export default function DownloadReportButton() {
  const onClick = () => {
    const a = document.createElement("a");
    a.href = `${import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000"}/reports/latest`;
    a.click();
  };
  return (
    <button onClick={onClick} style={{
        padding: "6px 10px",
        width: "auto"
    }}>
      Download KPI Report (.xlsx)
    </button>
  );
}
