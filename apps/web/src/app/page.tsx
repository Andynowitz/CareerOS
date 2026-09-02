import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ maxWidth: 720, margin: "80px auto", padding: 24 }}>
      <h1>CareerOS</h1>
      <p>
        Phase 1 foundation is running: monorepo, Docker, PostgreSQL, Redis,
        FastAPI and Better Auth.
      </p>
      <p>
        <Link href="/login">Log in</Link>
      </p>
    </main>
  );
}
