import MachinesTable from "./components/MachinesTable";

export default function App() {
  return (
    <div style={{ maxWidth: 960, margin: "40px auto", fontFamily: "Inter, system-ui, Arial" }}>
      <h1>Factory Data Dashboard</h1>
      <p style={{ color: "#555" }}>
        Minimal MVP: lists machines from Flask API and shows logs per machine.
      </p>
      <MachinesTable />
    </div>
  );
}
