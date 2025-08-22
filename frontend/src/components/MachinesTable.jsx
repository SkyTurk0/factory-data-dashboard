import { useEffect, useState } from "react";
import { getMachines, getLogs } from "../lib/api";

export default function MachinesTable() {
  const [machines, setMachines] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load machines once on mount
  useEffect(() => {
    (async () => {
      try {
        const data = await getMachines();
        setMachines(data);
      } catch (e) {
        setError(String(e));
      }
    })();
  }, []);

  // Fetch logs for a selected machine
  const loadLogs = async (id) => {
    setSelectedId(id);
    setLoading(true);
    setError("");
    try {
      const data = await getLogs(id);
      setLogs(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: 16 }}>
      <h2>Machines</h2>

      {error && <div style={{ color: "crimson" }}>{error}</div>}

      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>ID</th>
            <th style={{ textAlign: "left" }}>Name</th>
            <th style={{ textAlign: "left" }}>Status</th>
            <th>Logs</th>
          </tr>
        </thead>
        <tbody>
          {machines.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td>
              <td>{m.name}</td>
              <td>
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: 12,
                    background:
                      m.status === "Running"
                        ? "#d1fae5"
                        : m.status === "Idle"
                        ? "#e5e7eb"
                        : "#fee2e2",
                    border: "1px solid #ddd",
                  }}
                >
                  {m.status}
                </span>
              </td>
              <td>
                <button onClick={() => loadLogs(m.id)} disabled={loading}>
                  {loading && m.id === selectedId ? "Loading…" : "View Logs"}
                </button>
              </td>
            </tr>
          ))}

          {machines.length === 0 && (
            <tr>
              <td colSpan="4">No machines found.</td>
            </tr>
          )}
        </tbody>
      </table>

      <div>
        <h3>Logs {selectedId ? `(Machine ${selectedId})` : ""}</h3>
        {loading && <div>Loading logs…</div>}
        {!loading && selectedId && logs.length === 0 && <div>No logs.</div>}
        {!loading && logs.length > 0 && (
          <table border="1" cellPadding="6" style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>ID</th>
                <th style={{ textAlign: "left" }}>Timestamp</th>
                <th style={{ textAlign: "left" }}>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id}>
                  <td>{l.id}</td>
                  <td>{l.timestamp}</td>
                  <td>{l.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
