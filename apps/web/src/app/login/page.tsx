"use client";

import { FormEvent, useState } from "react";
import { authClient } from "@/lib/auth-client";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const result = await authClient.signIn.email({ email, password });

    if (result.error) {
      setError(result.error.message ?? "Unable to sign in.");
      return;
    }

    window.location.assign("/dashboard");
  }

  return (
    <main className="auth-page">
      <section className="auth-aside"><Link href="/" className="brand"><span className="brand-mark">C</span> CareerOS</Link><div><h1>Your next opportunity starts with clarity.</h1><p>One calm workspace for every application, conversation, and career move.</p></div><small>© CareerOS</small></section>
      <section className="auth-form-wrap"><div className="auth-card">
      <h1>Welcome back</h1>
      <p>Sign in to pick up where you left off.</p>
      <form onSubmit={handleSubmit} className="auth-form">
        <label>
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label>
          Password
          <input
            required
            type="password"
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <p role="alert">{error}</p> : null}
        <button type="submit">Log in to CareerOS</button>
      </form>
      <p className="auth-switch">New to CareerOS? <Link href="/register">Create an account</Link></p>
      </div></section>
    </main>
  );
}
