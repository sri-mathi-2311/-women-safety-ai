import { Outlet, NavLink, Link } from 'react-router-dom'
import '../styles/marketing.css'

const nav = [
  { to: '/', label: 'Home' },
  { to: '/about', label: 'About' },
  { to: '/why-us', label: 'Why Us' },
  { to: '/services', label: 'Services' },
  { to: '/contact', label: 'Contact' },
]

export default function SiteLayout() {
  return (
    <div className="site-root font-sans text-stone-200 antialiased">
      <a href="#main" className="skip-link">
        Skip to content
      </a>

      <header className="site-header">
        <div className="site-header-inner">
          <Link to="/" className="site-logo group">
            <img src="/women_safety_logo.png" alt="Logo" style={{ width: '36px', height: '36px', borderRadius: '8px', objectFit: 'cover' }} aria-hidden="true" />
            <span className="site-logo-text">
              <span className="block text-[0.65rem] uppercase tracking-[0.35em] text-amber-200/90">Women Safety</span>
              <span className="font-display text-xl tracking-tight text-stone-50 md:text-2xl">AI Platform</span>
            </span>
          </Link>

          <nav className="site-nav" aria-label="Primary">
            {nav.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `site-nav-link ${isActive ? 'site-nav-link--active' : ''}`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>

          <Link to="/console" className="site-cta">
            Live Console
          </Link>
        </div>
      </header>

      <main id="main">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="site-footer-inner">
          <p className="text-sm text-stone-500">
            © {new Date().getFullYear()} Women Safety AI. Crafted for safer campuses and public spaces.
          </p>
          <Link to="/console" className="text-sm text-amber-200/80 underline-offset-4 hover:text-amber-100 hover:underline">
            Operator console
          </Link>
        </div>
      </footer>
    </div>
  )
}
