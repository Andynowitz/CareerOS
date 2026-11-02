"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { authClient } from "@/lib/auth-client";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await authClient.signUp.email({
      name,
      email,
      password,
    });

    setLoading(false);

    if (error) {
      setError(error.message ?? "Registration failed.");
      return;
    }

    window.location.href = "/dashboard";
  }

  return (
    <main className="auth-page">
      <section className="auth-aside"><Link href="/" className="brand"><span className="brand-mark">C</span> CareerOS</Link><div><h1>Build a search that moves with you.</h1><p>Track the details, focus on the moments that matter, and make your next move with confidence.</p></div><small>© CareerOS</small></section>
      <section className="auth-form-wrap"><div className="auth-card">
      <h1>Create your workspace</h1>
      <p>Start organizing your job search in minutes.</p>

      <form
        onSubmit={handleSubmit}
        className="auth-form"
      >
        <label>
          Name
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
            autoComplete="name"
          />
        </label>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />
        </label>

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="auth-switch">Already have an account? <Link href="/login">Sign in</Link></p>
      </div></section>
    </main>
  );
}
