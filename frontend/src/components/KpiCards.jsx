import { useEffect, useState } from "react";
import { getKpis } from "../lib/api";

export default function KpiCards() {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await getKpis(); // defaults to last 7 days
        setKpis(data);
      } catch (e) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const totals = kpis.reduce(
    (acc, it) => {
      acc.throughput += it.totalThroughput || 0;
      acc.errors += it.errorCount || 0;
      return acc;
    },
    { throughput: 0, errors: 0 }
  );

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, margin: "16px 0" }}>
      <Card title="Total Throughput (7d)" value={totals.throughput.toLocaleString()} loading={loading} err={err} />
      <Card title="Total Errors (7d)" value={totals.errors} loading={loading} err={err} />
      <Card title="Machines Reporting" value={kpis.length} loading={loading} err={err} />
    </div>
  );
}

function Card({ title, value, loading, err }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 12, color: "#666" }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 700, marginTop: 6 }}>
        {loading ? "…" : err ? "ERR" : value}
      </div>
    </div>
  );
}
