export default function Services() {
  return (
    <section className="section" style={{ paddingTop: 'clamp(5rem, 10vw, 8rem)', paddingBottom: '3rem', minHeight: '100vh', backgroundImage: 'linear-gradient(to bottom, rgba(16, 16, 20, 0.7), rgba(16, 16, 20, 0.95)), url(/services_bg.png)', backgroundSize: 'cover', backgroundAttachment: 'fixed', backgroundPosition: 'center' }}>
      <div className="section-inner">
        <p className="section-label">Services</p>
        <h1 className="section-title">We craft with mastery</h1>
        <p className="section-prose">
          Three pillars mirror how premium studios deliver end-to-end programs — adapted here for
          AI-assisted safety operations.
        </p>

        <div className="services-grid">
          <article className="service-card">
            <h3>Design &amp; integration</h3>
            <p>
              We help you map camera coverage, threat scenarios, and escalation paths to the platform’s
              decision stack — from concept to a console your team can run with confidence.
            </p>
            <ul>
              <li>Workflow design for reviewers and supervisors</li>
              <li>Environment profiles (campus, workspace, public)</li>
              <li>Alignment with your alerting and SMS policies</li>
            </ul>
          </article>

          <article className="service-card">
            <h3>Flexible deployment</h3>
            <p>
              Run the stack on your hardware with deterministic, offline-friendly behavior — blending
              automation with the precision your institution requires.
            </p>
            <ul>
              <li>API-first dashboard and WebSocket realtime channel</li>
              <li>Metadata-centric storage for alerts and labels</li>
              <li>Scales from pilot rooms to multi-site programs</li>
            </ul>
          </article>

          <article className="service-card">
            <h3>Communication &amp; events</h3>
            <p>
              Turn detections into drills, tabletop exercises, and stakeholder reporting — we tie
              signals, narratives, and training into one cohesive story.
            </p>
            <ul>
              <li>Tabletop scenarios from live alert patterns</li>
              <li>Reviewer coaching with exported label sets</li>
              <li>Executive summaries grounded in triage history</li>
            </ul>
          </article>
        </div>
      </div>
    </section>
  )
}
