import MachinesTable from "./components/MachinesTable";
import KpiCards from "./components/KpiCards";
import ErrorsBarChart from "./components/ErrorsBarChart";
import ThroughputLineChart from "./components/ThroughputLineChart";

export default function App() {
  return (
    <div style={{ maxWidth: 1100, margin: "40px auto", fontFamily: "Inter, system-ui, Arial" }}>
      <h1>Factory Data Dashboard</h1>
      <p style={{ color: "#555" }}>
        KPI overview, recent errors, and machine logs. Backend: Flask + SQL Server (T-SQL procs).
      </p>

      <ThroughputLineChart />
      <KpiCards />
      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 16 }}>
        <div>
          <MachinesTable />
        </div>
        <div>
          <ErrorsBarChart />
        </div>
      </div>
    </div>
  );
}
