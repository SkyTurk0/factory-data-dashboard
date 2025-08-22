const BASE = "http://127.0.0.1:5000";  // Your Flask API base URL

// Fetch list of machines
export async function getMachines() {
  const res = await fetch(`${BASE}/machines`);
  if (!res.ok) throw new Error("Failed to fetch machines");
  return res.json();
}

// Fetch logs for one machine
export async function getLogs(machineId) {
  const res = await fetch(`${BASE}/logs/${machineId}`);
  if (!res.ok) throw new Error("Failed to fetch logs");
  return res.json();
}
