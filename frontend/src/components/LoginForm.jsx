import { useEffect, useState } from "react";
import { login } from "../lib/api";
import { saveAuth, clearAuth, getUser, AUTH_EVENT } from "../lib/auth";

export default function LoginForm({ onLogin }) {
  const existing = getUser();
  const [username, setUsername] = useState(existing?.username || "");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    const onChange = () => {
      const u = getUser();
      if (!u) { setUsername(""); setPassword(""); setErr(""); }
    };
    window.addEventListener(AUTH_EVENT, onChange);
    return () => window.removeEventListener(AUTH_EVENT, onChange);
  }, []);

  const doLogin = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const res = await login(username, password);
      saveAuth(res);
      onLogin?.(res.user);
    } catch (e) {
      setErr(String(e));
    }
  };

  const doLogout = () => {
    clearAuth();
    onLogin?.(null);
  };

  return (
    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
      {!existing ? (
        <form onSubmit={doLogin} style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
          <input placeholder="password" value={password} onChange={e => setPassword(e.target.value)} type="password" />
          <button type="submit">Login</button>
          {err && <span style={{ color: "crimson" }}>{err}</span>}
        </form>
      ) : (
        <>
          <span>Signed in as <strong>{existing.username}</strong> ({existing.role})</span>
          <button onClick={doLogout}>Logout</button>
        </>
      )}
    </div>
  );
}
