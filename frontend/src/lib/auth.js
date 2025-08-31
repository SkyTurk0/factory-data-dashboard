const KEY = "factory_auth";
const EVT = "auth:changed";

export function saveAuth({ token, user }) {
  localStorage.setItem(KEY, JSON.stringify({ token, user }));
  window.dispatchEvent(new Event(EVT));
}

export function clearAuth() {
  localStorage.removeItem(KEY);
  window.dispatchEvent(new CustomEvent(EVT));
}

export function getAuth() {
  try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch { return null; }
}

export function getToken() { return getAuth()?.token || null; }
export function getUser() { return getAuth()?.user || null; }
export const AUTH_EVENT = EVT;