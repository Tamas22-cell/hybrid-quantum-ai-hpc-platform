"use client";

import { useState } from "react";

export default function LoginPage() {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Sign in failed");
      const next = new URLSearchParams(window.location.search).get("next");
      window.location.replace(next?.startsWith("/") && !next.startsWith("//") ? next : "/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <a className="brand-link" href="/">HYBRID COMPUTE / HPC</a>
      <section className="auth-card">
        <small>YOUR WORKSPACE</small>
        <h1>Sign in</h1>
        <p>Access your workloads and benchmark history.</p>
        <form onSubmit={submit}>
          <label>Email<input name="email" type="email" autoComplete="email" required maxLength={254} /></label>
          <label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={128} /></label>
          {error && <p role="alert">{error}</p>}
          <button disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        </form>
        <p className="auth-switch">New here? <a href="/register">Create an account</a></p>
      </section>
    </main>
  );
}
