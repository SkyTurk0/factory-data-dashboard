import { useEffect ,useState } from "react";
import { getAuth, AUTH_EVENT } from "./lib/auth";
import MachinesTable from "./components/MachinesTable";
import KpiCards from "./components/KpiCards";
import ErrorsBarChart from "./components/ErrorsBarChart";
import ThroughputLineChart from "./components/ThroughputLineChart";
import DownloadReportButton from "./components/DownloadReportButton";
import LoginForm from "./components/LoginForm";

export default function App() {

  const [auth, setAuth] = useState(() => getAuth()); // {token, user} or null

  useEffect(() => {
    const onChange = () => setAuth(getAuth());
    window.addEventListener(AUTH_EVENT, onChange);
    return () => window.removeEventListener(AUTH_EVENT, onChange);
  }, []);

  return (
    <div style={{ maxWidth: 1100, margin: "40px auto", fontFamily: "Inter, system-ui, Arial" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" } }>
        <h1 style={{ margin: 0 }}>Factory Data Dashboard</h1>
        <LoginForm />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <p style={{ color: "#555", margin: 0 }}>
          KPI overview, recent errors, and machine logs. Backend: Flask + SQL Server (T-SQL procs).
        </p>
        <DownloadReportButton />
      </div>

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
