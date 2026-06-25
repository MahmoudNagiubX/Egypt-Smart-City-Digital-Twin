import React from 'react';
import { motion } from 'motion/react';

interface WelcomePageProps {
  onOpenDashboard: () => void;
}

export const WelcomePage: React.FC<WelcomePageProps> = ({ onOpenDashboard }) => {
  return (
    <div className="stitch-page flex flex-col items-center" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* Atmospheric background blobs */}
      <div className="stitch-bg-cloud-1" aria-hidden="true" />
      <div className="stitch-bg-cloud-2" aria-hidden="true" />

      {/* Floating Nav Pill */}
      <nav className="stitch-pill flex items-center gap-8 px-6 py-3 sticky top-6 z-50 mx-auto mt-6" role="navigation" aria-label="Main navigation">
        {/* Logo */}
        <div
          className="flex items-center justify-center w-8 h-8 rounded-full shadow-sm"
          style={{ background: 'linear-gradient(135deg, #006688 0%, #83fba5 100%)' }}
          aria-hidden="true"
        >
          <div className="w-3 h-3 bg-white rounded-full" style={{ mixBlendMode: 'overlay' }} />
        </div>
        {/* Links */}
        <div className="flex items-center gap-6">
          <a href="#" className="text-sm font-semibold" style={{ color: 'var(--stitch-primary)' }}>Home</a>
          <a
            href="#features"
            className="text-sm"
            style={{ color: 'var(--stitch-text-muted)' }}
            onMouseOver={e => (e.currentTarget.style.color = 'var(--stitch-text-charcoal)')}
            onMouseOut={e => (e.currentTarget.style.color = 'var(--stitch-text-muted)')}
          >Features</a>
          <a
            href="#model"
            className="text-sm"
            style={{ color: 'var(--stitch-text-muted)' }}
            onMouseOver={e => (e.currentTarget.style.color = 'var(--stitch-text-charcoal)')}
            onMouseOut={e => (e.currentTarget.style.color = 'var(--stitch-text-muted)')}
          >Model</a>
          <a
            href="#how"
            className="text-sm"
            style={{ color: 'var(--stitch-text-muted)' }}
            onMouseOver={e => (e.currentTarget.style.color = 'var(--stitch-text-charcoal)')}
            onMouseOut={e => (e.currentTarget.style.color = 'var(--stitch-text-muted)')}
          >How it works</a>
        </div>
      </nav>

      {/* Hero Section */}
      <motion.main
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="flex flex-col items-center w-full max-w-4xl mx-auto mt-16 px-4 text-center z-10"
      >
        <h1
          className="max-w-3xl"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 'clamp(36px, 5vw, 56px)',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
            color: 'var(--stitch-text-charcoal)',
          }}
        >
          Stay ahead with a{' '}<br />
          <span className="stitch-marker-highlight">safer</span> city route plan
        </h1>
        <p
          className="mt-6 max-w-xl mx-auto"
          style={{ fontSize: 16, color: 'var(--stitch-text-muted)', lineHeight: 1.6 }}
        >
          Visualize weather risk, traffic pressure, and emergency routes across Nasr City — faster and smarter.
        </p>
        <div className="flex flex-row items-center justify-center gap-4 mt-8">
          <button
            id="welcome-open-dashboard"
            onClick={onOpenDashboard}
            className="font-semibold shadow-sm transition-colors"
            style={{
              background: '#1A1C1E',
              color: 'white',
              padding: '12px 32px',
              borderRadius: 12,
              fontSize: 14,
              border: 'none',
              cursor: 'pointer',
            }}
            onMouseOver={e => ((e.currentTarget as HTMLButtonElement).style.background = '#000')}
            onMouseOut={e => ((e.currentTarget as HTMLButtonElement).style.background = '#1A1C1E')}
          >
            Open Live Map
          </button>
          <button
            id="welcome-see-how"
            className="font-semibold shadow-sm transition-colors"
            style={{
              background: 'white',
              color: '#1A1C1E',
              padding: '12px 32px',
              borderRadius: 12,
              fontSize: 14,
              border: '1px solid #1A1C1E',
              cursor: 'pointer',
            }}
            onMouseOver={e => ((e.currentTarget as HTMLButtonElement).style.background = '#f9f9f9')}
            onMouseOut={e => ((e.currentTarget as HTMLButtonElement).style.background = 'white')}
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          >
            See how it works
          </button>
        </div>

        {/* 3D Folded Map Illustration Area */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
          className="mt-16 relative w-full max-w-3xl mx-auto flex justify-center"
        >
          <img 
            className="w-full object-contain drop-shadow-xl" 
            alt="3D premium illustration of a folded paper map in soft green and blue tones" 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuC_LMFYxjJS9V6d9n3vWHh3vt9igJkl31nAoevS6Wc9Mhy0zaJB7Gca-S-97vFZB5hF4DXPOTU7KSPbniI-lkYTY_bTnojW1ULDZpboH2oApORZW7xFTE82TA9WJty-aafNSJ9M-7j1ThICRzeS0lpgmIHh_cFKY1YdlvZyEb0tbS5jgMwj0xwYiYLFwWtFGeMsFxGASuEgfDdjTpAWdxOYTwEbLVdgwylQJ9_rWqCRQCpCGK1vb4DPrF4OVWazgS1aqcSpbC40Pg" 
            style={{ maxHeight: 400 }}
          />
        </motion.div>
      </motion.main>

      {/* Features Section */}
      <section id="features" className="w-full max-w-5xl mx-auto px-4 mt-24">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ textAlign: 'center', fontFamily: "'Inter', sans-serif", fontSize: 24, fontWeight: 600, color: 'var(--stitch-text-charcoal)', marginBottom: '1.5rem' }}
        >
          What it does
        </motion.h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { emoji: '🌧️', title: 'Live Rain Risk', desc: 'Real-time ML risk scores across all Nasr City zones based on live weather.' },
            { emoji: '🛣️', title: 'Safer Routing', desc: 'Weather-aware routing engine avoids high-risk zones for emergency dispatch.' },
            { emoji: '🔍', title: 'Explainable AI', desc: 'Understand why an area is risky and why a route was recommended.' },
            { emoji: '📍', title: 'Smart Search', desc: 'Find streets, hospitals, mosques, malls — and fly to them on the map.' },
          ].map((feat, i) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="stitch-card flex flex-col gap-3"
            >
              <span style={{ fontSize: 28 }}>{feat.emoji}</span>
              <h3 style={{ fontWeight: 600, fontSize: 15, color: 'var(--stitch-text-charcoal)', margin: 0 }}>{feat.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--stitch-text-muted)', margin: 0, lineHeight: 1.55 }}>{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-16 mb-8 px-4 text-center" style={{ fontSize: 11, color: 'var(--stitch-text-muted)' }}>
        Decision-support prototype only. Not an official flood forecast or emergency dispatch system.
      </footer>
    </div>
  );
};

export default WelcomePage;
