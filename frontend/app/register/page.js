"use client";

import { useState } from "react";

export default function RegisterPage() {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Registration failed");
      window.location.replace("/");
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
        <small>PUBLIC REGISTRATION</small>
        <h1>Create account</h1>
        <p>Your jobs and saved results stay private to your account.</p>
        <form onSubmit={submit}>
          <label>Email<input name="email" type="email" autoComplete="email" required maxLength={254} /></label>
          <label>Password<input name="password" type="password" autoComplete="new-password" required minLength={12} maxLength={128} /></label>
          <small>Use at least 12 characters.</small>
          {error && <p role="alert">{error}</p>}
          <button disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
        </form>
        <p className="auth-switch">Already registered? <a href="/login">Sign in</a></p>
      </section>
    </main>
  );
}
