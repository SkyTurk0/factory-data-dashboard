import { useEffect, useMemo, useState } from "react";
import { getThroughput, getMachines } from "../lib/api";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

export default function ThroughputLineChart() {
  const [bucket, setBucket] = useState("hour");         // "hour" | "day"
  const [machineId, setMachineId] = useState("");       // "" = all
  const [machines, setMachines] = useState([]);
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(() => {
    // default collapsed on narrow screens
    if (typeof window !== "undefined") return window.innerWidth < 900;
    return false;
  });

  // Load machine list for the dropdown once
  useEffect(() => {
    (async () => {
      try {
        const m = await getMachines();
        setMachines(m);
      } catch (e) {
        console.error(e);
      } 
    })();
  }, []);

  // Fetch throughput whenever filters change
  useEffect(() => {
    if (collapsed) return;
    (async () => {
      try {
        setLoading(true);
        setErr("");
        const res = await getThroughput({
          bucket,
          machineId: machineId ? Number(machineId) : undefined,
        });
        const labels = res.points.map(p => new Date(p.ts).toLocaleString());
        const values = res.points.map(p => Number(p.throughput) || 0);

        setData({
          labels,
          datasets: [
            {
              label: `Throughput (${bucket})${machineId ? ` — Machine ${machineId}` : ""}`,
              data: values,
              tension: 0.25,
            },
          ],
        });
      } catch (e) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [bucket, machineId, collapsed]);

  const machineOptions = useMemo(
    () => [{ id: "", name: "All machines" }, ...machines],
    [machines]
  );

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <h3 style={{ margin: 0 }}>Throughput Over Time</h3>

        <div style={{ display: "flex", gap: 8 }}>
          {/* Bucket toggle */}
          <select value={bucket} onChange={e => setBucket(e.target.value)} disabled={collapsed}>
            <option value="hour">Per hour</option>
            <option value="day">Per day</option>
          </select>

          {/* Machine filter */}
          <select value={machineId} onChange={e => setMachineId(e.target.value)} disabled={collapsed}>
            {machineOptions.map(m => (
              <option key={m.id || "all"} value={m.id}>{m.name}</option>
            ))}
          </select>
           <button onClick={() => setCollapsed(c => !c)} style={{ padding: "6px 10px" }}>
            {collapsed ? "Show" : "Hide"}
          </button>
        </div>
      </div>

      {!collapsed && (
        <>
          {loading && <div style={{ marginTop: 8 }}>Loading throughput…</div>}
          {err && <div style={{ color: "crimson", marginTop: 8 }}>{err}</div>}
          {!loading && !err && data && data.labels.length > 0 && (
            <div style={{ height: 320, marginTop: 8 }}>
              <Line
                data={data}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 }, grid: { drawBorder: false } },
                    x: { grid: { display: false, drawBorder: false } },
                  },
                  plugins: { legend: { display: true } },
                }}
              />
            </div>
          )}
          {!loading && !err && data && data.labels.length === 0 && (
            <div style={{ marginTop: 8 }}>No throughput data for this selection.</div>
          )}
        </>
      )}
    </div>
  );
}