import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Contact() {
  const [sent, setSent] = useState(false)

  const onSubmit = (e) => {
    e.preventDefault()
    setSent(true)
  }

  return (
    <section className="section" style={{ paddingTop: 'clamp(5rem, 10vw, 8rem)', paddingBottom: '3rem', minHeight: '100vh', backgroundImage: 'linear-gradient(to bottom, rgba(16, 16, 20, 0.6), rgba(16, 16, 20, 0.9)), url(/contact_bg.png)', backgroundSize: 'cover', backgroundAttachment: 'fixed', backgroundPosition: 'center' }}>
      <div className="section-inner">
        <p className="section-label">Contact</p>
        <h1 className="section-title">Let’s craft something that carries meaning</h1>
        <p className="section-prose">
          Share your campus or venue context — we’ll follow up with next steps for a pilot, technical
          review, or partnership conversation.
        </p>

        <div className="contact-grid">
          <dl className="contact-card">
            <dt>Studio</dt>
            <dd>Women Safety AI</dd>
            <dt>Console</dt>
            <dd>
              Operators can open the{' '}
              <Link to="/console" className="text-amber-200 underline-offset-4 hover:underline">
                live console
              </Link>{' '}
              when the API is running locally.
            </dd>
            <dt>Response time</dt>
            <dd>We typically reply within two business days.</dd>
          </dl>

          <div className="contact-card">
            {sent ? (
              <p style={{ margin: 0, color: 'rgba(214, 211, 209, 0.95)', lineHeight: 1.6 }}>
                Thank you — your message is noted. (Demo form: connect this to your backend or email
                service when ready.)
              </p>
            ) : (
              <form className="contact-form" onSubmit={onSubmit}>
                <label htmlFor="name">Name</label>
                <input id="name" name="name" required autoComplete="name" placeholder="Your name" />

                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@organization.org"
                />

                <label htmlFor="msg">Message</label>
                <textarea id="msg" name="message" required placeholder="Tell us about your deployment…" />

                <button type="submit" className="btn-primary-lg" style={{ width: '100%' }}>
                  Send message
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
