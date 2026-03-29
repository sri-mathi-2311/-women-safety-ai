export default function About() {
  return (
    <section className="section" style={{ paddingTop: 'clamp(5rem, 10vw, 8rem)', paddingBottom: '3rem', minHeight: '100vh', backgroundImage: 'linear-gradient(to bottom, rgba(16, 16, 20, 0.7), rgba(16, 16, 20, 0.95)), url(/about_bg.png)', backgroundSize: 'cover', backgroundAttachment: 'fixed', backgroundPosition: 'center' }}>
      <div className="section-inner">
        <p className="section-label">About</p>
        <h1 className="section-title">An ecosystem uniting care and technology</h1>
        <div className="section-prose">
          <p>
            This platform was conceived as more than a detector — it is an <strong>integrated ecosystem</strong>{' '}
            that connects perception, decision intelligence, and human review. We believe women’s
            safety in shared spaces deserves tooling that is both powerful and respectful: fast when
            it matters, quiet when it does not, and always oriented toward accountability.
          </p>
          <p>
            Our stack combines computer vision, pose-aware cues, and a multi-agent decision layer
            that fuses specialized risk signals into a single, interpretable threat assessment.
            Operators see confidence, severity, and evidence in one place — so escalation is a
            choice informed by data, not a guess in a noisy feed.
          </p>
          <p>
            We are committed to a <strong>metadata-first</strong> workflow: the console is designed
            around events, signals, and labels rather than long-term image retention — aligning
            technical capability with privacy expectations in real deployments.
          </p>
        </div>
      </div>
    </section>
  )
}
