import { useEffect, useState } from "react";
import { getLatestLogs } from "../lib/api";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function ErrorsBarChart() {
  const [chartData, setChartData] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const logs = await getLatestLogs({ top: 200 });

        // Count ERRORs by machine safely
        const counts = new Map();
        for (const l of logs) {
          if (String(l?.type ?? "").toUpperCase() !== "ERROR") continue;
          const machineId = Number(l?.machineId ?? NaN);
          const machineName = String(l?.machineName ?? `Machine ${machineId || "?"}`);
          const key = `${machineId}:${machineName}`;
          counts.set(key, (counts.get(key) || 0) + 1);
        }

        const labels = Array.from(counts.keys()).map(k => k.split(":")[1]);
        const values = Array.from(counts.values()).map(v => Number(v) || 0);

        setChartData({
          labels,
          datasets: [
            {
              label: "Errors (recent)",
              data: values,
            },
          ],
        });
      } catch (e) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div>Loading error chart…</div>;
  if (err) return <div style={{ color: "crimson" }}>{err}</div>;
  if (!chartData || chartData.labels.length === 0) return <div>No recent errors.</div>;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Recent Errors by Machine</h3>
      {/* Give the canvas a fixed height when responsive */}
      <div style={{ height: 300 }}>
        <Bar
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false, // respect the 300px wrapper
            scales: {
              y: {
                beginAtZero: true,
                ticks: { precision: 0 },
                grid: { drawBorder: false },
              },
              x: {
                ticks: { autoSkip: false, maxRotation: 0, minRotation: 0 },
                grid: { display: false, drawBorder: false },
              },
            },
            plugins: { legend: { display: true } },
          }}
        />
      </div>
    </div>
  );
}
