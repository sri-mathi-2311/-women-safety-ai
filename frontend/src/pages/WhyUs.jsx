export default function WhyUs() {
  return (
    <section className="section" style={{ paddingTop: 'clamp(5rem, 10vw, 8rem)', paddingBottom: '3rem', minHeight: '100vh', backgroundImage: 'linear-gradient(to bottom, rgba(16, 16, 20, 0.7), rgba(16, 16, 20, 0.95)), url(/whyus_bg.png)', backgroundSize: 'cover', backgroundAttachment: 'fixed', backgroundPosition: 'center' }}>
      <div className="section-inner">
        <p className="section-label">Why us</p>
        <h1 className="section-title">Details that matter</h1>
        <div className="section-prose">
          <p>
            Public safety products often fail in one of two ways: they either overwhelm teams with
            alerts, or they hide so much complexity that no one trusts the output. Our system sits in
            the middle — <strong>structured fusion</strong> with <strong>transparent scores</strong>{' '}
            and a <strong>reviewer-first</strong> triage queue.
          </p>
        </div>

        <div className="pillars-grid" style={{ marginTop: '2.5rem' }}>
          {[
            {
              title: 'Multi-agent fusion',
              text: 'Object, pose, crowd, motion, trajectory, and temporal agents contribute weighted evidence — not a single brittle rule.',
            },
            {
              title: 'Operational tempo',
              text: 'WebSocket-backed status, live feed, and snapshot statistics keep the room aligned during incidents and drills.',
            },
            {
              title: 'Calibration-ready',
              text: 'Environment profiles and threshold tuning help you match sensitivity to campus, workspace, or public venue contexts.',
            },
            {
              title: 'Human in the loop',
              text: 'Export reviewer labels for training and audit — closing the loop between the field and your safety program.',
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
  )
}
