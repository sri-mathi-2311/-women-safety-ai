import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <>
      <section className="page-hero" style={{ backgroundImage: 'linear-gradient(to bottom, rgba(16, 16, 20, 0.4), rgba(16, 16, 20, 1)), url(/hero_ai_surveillance.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}>
        <div className="page-hero-inner">
          <p className="hero-kicker">An integrated ecosystem for public safety</p>
          <h1 className="hero-title">
            Where vigilance
            <br />
            becomes <em>action</em>
          </h1>
          <p className="hero-lead">
            Our platform unites AI perception, multi-agent reasoning, and human review into one calm
            operations experience — so teams can respond with confidence, not guesswork.
          </p>
          <div className="hero-actions">
            <Link to="/contact" className="btn-primary-lg">
              Get started
            </Link>
            <Link to="/why-us" className="btn-ghost-lg">
              Why us
            </Link>
          </div>
        </div>
      </section>

      <div className="stats-strip">
        {[
          { v: '7+', l: 'Specialized AI signals fused' },
          { v: '24/7', l: 'Designed for continuous ops' },
          { v: '100%', l: 'Metadata-first privacy stance' },
          { v: '∞', l: 'Scalable review workflows' },
        ].map((s) => (
          <div key={s.l} className="stat-card">
            <div className="stat-value">{s.v}</div>
            <div className="stat-label">{s.l}</div>
          </div>
        ))}
      </div>

      <section className="section">
        <div className="section-inner">
          <p className="section-label">Our approach to mastery</p>
          <h2 className="section-title">We protect with clarity</h2>
          <p className="section-prose">
            Like leading craft studios that blend design and manufacturing, we fuse machine
            intelligence with operator judgment — turning raw video into structured evidence,
            reviewer labels, and audit-ready history.
          </p>

          <div className="pillars-grid">
            {[
              {
                title: 'Precision as a mindset',
                text: 'Every alert is scored, attributed, and explainable so your team sees the “why” behind the signal.',
              },
              {
                title: 'Innovation as identity',
                text: 'Multi-agent fusion and temporal consistency reduce noise while surfacing patterns humans might miss.',
              },
              {
                title: 'Impact as purpose',
                text: 'Built for campuses, workplaces, and public venues where safety outcomes depend on timely, trusted action.',
              },
              {
                title: 'Partnership as value',
                text: 'Your reviewers train the loop: triage queues and exports connect the field to continuous improvement.',
              },
            ].map((p) => (
              <article key={p.title} className="pillar-card">
                <h3>{p.title}</h3>
                <p>{p.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <div className="cta-band">
        <h2>Where your safety program becomes an experience</h2>
        <p>
          Let’s build something that carries meaning for your community — clear signals, responsible
          oversight, and a console your team actually wants to use.
        </p>
        <Link to="/contact" className="btn-primary-lg">
          Start your journey
        </Link>
      </div>
    </>
  )
}
