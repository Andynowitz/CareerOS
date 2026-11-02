import Link from "next/link";

const navigation = [
  { href: "/dashboard", label: "Overview", icon: "⌂" },
  { href: "/dashboard/jobs", label: "Applications", icon: "▤" },
  { href: "/dashboard/kanban", label: "Pipeline", icon: "▥" },
  { href: "/dashboard/resumes", label: "Resumes", icon: "▧" },
];

export default function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brand-mark">C</span> CareerOS
        </Link>
        <div className="sidebar-label">Workspace</div>
        <nav>
          {navigation.map((item) => (
            <Link key={item.href} href={item.href}>
              <span aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="sidebar-foot">A calmer way to navigate your career.</div>
      </aside>
      <div className="app-content">
        <header className="mobile-topbar">
          <Link href="/" className="brand"><span className="brand-mark">C</span> CareerOS</Link>
          <Link href="/dashboard/jobs" className="button button-primary">Add application</Link>
        </header>
        <div className="app-main">{children}</div>
      </div>
    </div>
  );
}
