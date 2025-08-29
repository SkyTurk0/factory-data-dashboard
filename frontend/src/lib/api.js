const BASE = import.meta.env.VITE_API_BASE ?? "https://127.0.0.1:5000";  // Flask API base URL

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

export async function getLatestLogs({ top = 50, machineId } = {}) {
  const url = new URL(`${BASE}/sp/latest-logs`);
  url.searchParams.set("top", String(top));
  if (machineId) url.searchParams.set("machineId", String(machineId));
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch latest logs");
  return res.json();
}

export async function getKpis({ fromISO, toISO} = {}) {
  const url = new URL(`${BASE}/sp/kpis`);
  if (fromISO) url.searchParams.set("from", fromISO);
  if (toISO) url.searchParams.set("to", toISO);
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch KPIs");
  return res.json();
}

export async function getThroughput({ fromISO, toISO, bucket = "hour", machineId } = {}) {
  const url = new URL(`${BASE}/metrics/throughput`);
  if (fromISO) url.searchParams.set("from", fromISO);
  if (toISO) url.searchParams.set("to", toISO);
  if (bucket) url.searchParams.set("bucket", bucket);
  if (machineId) url.searchParams.set("machineId", String(machineId));
  const r = await fetch(url);
  if (!r.ok) throw new Error("Failed to fetch throughput");
  return r.json();
}
