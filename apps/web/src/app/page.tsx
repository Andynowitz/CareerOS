import Link from "next/link";

export default function HomePage() {
  return (
    <div className="landing">
      <header className="site-header">
        <Link href="/" className="brand"><span className="brand-mark">C</span> CareerOS</Link>
        <nav className="nav-links">
          <Link href="#features">Why it works</Link>
          <Link href="/login">Sign in</Link>
          <Link href="/register" className="button button-primary">Get started</Link>
        </nav>
      </header>
      <main>
        <section className="hero">
          <div>
            <div className="eyebrow">Your career, organized</div>
            <h1>Turn the job search into <span>forward motion.</span></h1>
            <p className="hero-copy">Bring applications, resumes, and next steps into one focused workspace, so you can spend less time tracking work and more time finding the right role.</p>
            <div className="hero-actions">
              <Link href="/register" className="button button-primary">Create your workspace →</Link>
              <Link href="/login" className="button button-ghost">Already have an account?</Link>
            </div>
          </div>
          <div className="preview-window" aria-label="CareerOS dashboard preview">
            <div className="preview-top"><i /><i /><i /></div>
            <div className="preview-body">
              <div className="preview-side"><b /><span /><span /><span /><span /></div>
              <div className="preview-content">
                <strong>Good morning, Alex</strong>
                <p className="text-sm text-gray-500">Here’s your application pulse.</p>
                <div className="preview-stats"><div className="preview-stat"><small>Applications</small><b>24</b></div><div className="preview-stat"><small>Interviews</small><b>06</b></div><div className="preview-stat"><small>Offers</small><b>02</b></div></div>
                <div className="preview-list"><span /><span /><span /></div>
              </div>
            </div>
          </div>
        </section>
        <section id="features" className="feature-section">
          <div className="eyebrow">Everything in one place</div>
          <div className="feature-grid">
            <article className="feature-card"><div className="feature-icon">01</div><h2>See the full picture</h2><p>A clear dashboard turns a scattered search into a plan you can act on.</p></article>
            <article className="feature-card"><div className="feature-icon">02</div><h2>Keep momentum</h2><p>Move applications through your pipeline and always know what comes next.</p></article>
            <article className="feature-card"><div className="feature-icon">03</div><h2>Make better matches</h2><p>Keep your resume versions and role insights close when decisions matter.</p></article>
          </div>
        </section>
      </main>
      <footer className="site-footer">© 2025 · Built for your next chapter</footer>
    </div>
  );
}
