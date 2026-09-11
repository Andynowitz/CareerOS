import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await import("next/headers").then((module) => module.headers()),
  });

  if (!session) {
    redirect("/login");
  }

  return (
    <main style={{ maxWidth: 720, margin: "80px auto", padding: 24 }}>
      <h1>CareerOS Dashboard</h1>
      <p>Authenticated as {session.user.email}</p>
      <p>Phase 1 foundation is active.</p>
    </main>
  );
}
