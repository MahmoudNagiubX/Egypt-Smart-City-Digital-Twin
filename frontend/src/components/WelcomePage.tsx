import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface WelcomePageProps {
  onOpenDashboard: () => void;
}

export const WelcomePage: React.FC<WelcomePageProps> = ({ onOpenDashboard }) => {
  const [activeModal, setActiveModal] = useState<'features' | 'model' | 'how-it-works' | null>(null);

  return (
    <div className="stitch-page flex flex-col items-center h-screen max-h-screen overflow-hidden relative" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* Atmospheric background blobs */}
      <div className="stitch-bg-cloud-1" aria-hidden="true" />
      <div className="stitch-bg-cloud-2" aria-hidden="true" />

      {/* Floating Nav Pill */}
      <nav className="stitch-pill flex items-center gap-8 px-6 py-3 sticky top-6 z-50 mx-auto mt-6 shrink-0" role="navigation" aria-label="Main navigation">
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
          <button
            onClick={() => setActiveModal(null)}
            className="text-sm font-semibold cursor-pointer bg-transparent border-none p-0 transition-colors"
            style={{ color: activeModal === null ? 'var(--stitch-primary)' : 'var(--stitch-text-muted)' }}
            onMouseOver={e => { if (activeModal !== null) e.currentTarget.style.color = 'var(--stitch-text-charcoal)'; }}
            onMouseOut={e => { if (activeModal !== null) e.currentTarget.style.color = 'var(--stitch-text-muted)'; }}
          >
            Home
          </button>
          <button
            onClick={() => setActiveModal('features')}
            className="text-sm cursor-pointer bg-transparent border-none p-0 transition-colors"
            style={{ color: activeModal === 'features' ? 'var(--stitch-primary)' : 'var(--stitch-text-muted)', fontWeight: activeModal === 'features' ? 600 : 400 }}
            onMouseOver={e => { if (activeModal !== 'features') e.currentTarget.style.color = 'var(--stitch-text-charcoal)'; }}
            onMouseOut={e => { if (activeModal !== 'features') e.currentTarget.style.color = 'var(--stitch-text-muted)'; }}
          >
            Features
          </button>
          <button
            onClick={() => setActiveModal('model')}
            className="text-sm cursor-pointer bg-transparent border-none p-0 transition-colors"
            style={{ color: activeModal === 'model' ? 'var(--stitch-primary)' : 'var(--stitch-text-muted)', fontWeight: activeModal === 'model' ? 600 : 400 }}
            onMouseOver={e => { if (activeModal !== 'model') e.currentTarget.style.color = 'var(--stitch-text-charcoal)'; }}
            onMouseOut={e => { if (activeModal !== 'model') e.currentTarget.style.color = 'var(--stitch-text-muted)'; }}
          >
            Model
          </button>
          <button
            onClick={() => setActiveModal('how-it-works')}
            className="text-sm cursor-pointer bg-transparent border-none p-0 transition-colors"
            style={{ color: activeModal === 'how-it-works' ? 'var(--stitch-primary)' : 'var(--stitch-text-muted)', fontWeight: activeModal === 'how-it-works' ? 600 : 400 }}
            onMouseOver={e => { if (activeModal !== 'how-it-works') e.currentTarget.style.color = 'var(--stitch-text-charcoal)'; }}
            onMouseOut={e => { if (activeModal !== 'how-it-works') e.currentTarget.style.color = 'var(--stitch-text-muted)'; }}
          >
            How it works
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <motion.main
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="flex-1 flex flex-col items-center justify-center w-full max-w-4xl mx-auto px-4 text-center z-10 min-h-0"
      >
        <h1
          className="max-w-3xl"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 'clamp(28px, 4vw, 44px)',
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
          className="mt-4 max-w-xl mx-auto"
          style={{ fontSize: 'clamp(14px, 1.5vw, 15px)', color: 'var(--stitch-text-muted)', lineHeight: 1.5 }}
        >
          Visualize weather risk, traffic pressure, and emergency routes across Nasr City — faster and smarter.
        </p>
        <div className="flex flex-row items-center justify-center gap-4 mt-6">
          <button
            id="welcome-open-dashboard"
            onClick={onOpenDashboard}
            className="font-semibold shadow-sm transition-colors"
            style={{
              background: '#1A1C1E',
              color: 'white',
              padding: '10px 28px',
              borderRadius: 10,
              fontSize: 13,
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
            onClick={() => setActiveModal('how-it-works')}
            className="font-semibold shadow-sm transition-colors"
            style={{
              background: 'white',
              color: '#1A1C1E',
              padding: '10px 28px',
              borderRadius: 10,
              fontSize: 13,
              border: '1px solid #1A1C1E',
              cursor: 'pointer',
            }}
            onMouseOver={e => ((e.currentTarget as HTMLButtonElement).style.background = '#f9f9f9')}
            onMouseOut={e => ((e.currentTarget as HTMLButtonElement).style.background = 'white')}
          >
            See how it works
          </button>
        </div>

        {/* 3D Folded Map Illustration Area */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
          className="mt-8 relative w-full max-w-2xl mx-auto flex justify-center min-h-0 flex-1 items-center"
        >
          <img 
            className="w-full h-full max-h-[30vh] object-contain drop-shadow-xl" 
            alt="3D premium illustration of a folded paper map in soft green and blue tones" 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuC_LMFYxjJS9V6d9n3vWHh3vt9igJkl31nAoevS6Wc9Mhy0zaJB7Gca-S-97vFZB5hF4DXPOTU7KSPbniI-lkYTY_bTnojW1ULDZpboH2oApORZW7xFTE82TA9WJty-aafNSJ9M-7j1ThICRzeS0lpgmIHh_cFKY1YdlvZyEb0tbS5jgMwj0xwYiYLFwWtFGeMsFxGASuEgfDdjTpAWdxOYTwEbLVdgwylQJ9_rWqCRQCpCGK1vb4DPrF4OVWazgS1aqcSpbC40Pg" 
          />
        </motion.div>
      </motion.main>

      {/* Footer */}
      <footer className="mt-auto mb-4 px-4 text-center shrink-0" style={{ fontSize: 10, color: 'var(--stitch-text-muted)' }}>
        Decision-support prototype only. Not an official flood forecast or emergency dispatch system.
      </footer>

      {/* Glass Detail Modals */}
      <AnimatePresence>
        {activeModal && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/10 backdrop-blur-sm"
            onClick={() => setActiveModal(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              className="stitch-glass w-full max-w-2xl p-6 md:p-8 rounded-[24px] relative"
              style={{
                background: 'rgba(255, 255, 255, 0.88)',
                boxShadow: '0 20px 48px rgba(0, 66, 100, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.6)',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={() => setActiveModal(null)}
                className="absolute top-4 right-4 flex items-center justify-center w-8 h-8 rounded-full border border-black/5 hover:bg-black/5 text-text-charcoal cursor-pointer transition-colors"
                aria-label="Close modal"
              >
                ✕
              </button>

              {activeModal === 'features' && (
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-text-charcoal mb-5">Smart mobility features</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { emoji: '🌧️', title: 'Live Rain Risk', desc: 'View today’s model-estimated rain-impact zones across Nasr City.' },
                      { emoji: '🛣️', title: 'Safer Routing', desc: 'Compare the normal route with a weather-aware safer route.' },
                      { emoji: '🔍', title: 'Explainable AI', desc: 'Understand why an area is risky and why a route was recommended.' },
                      { emoji: '📍', title: 'Smart Search', desc: 'Search streets, places, hospitals, and zones directly from the map.' },
                    ].map((feat) => (
                      <div key={feat.title} className="p-4 rounded-xl border border-white/50 bg-white/40 shadow-xs flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{feat.emoji}</span>
                          <h3 className="font-semibold text-sm text-text-charcoal">{feat.title}</h3>
                        </div>
                        <p className="text-xs text-text-muted leading-relaxed">{feat.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeModal === 'model' && (
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-text-charcoal mb-5">How the AI model helps</h2>
                  <div className="flex flex-col gap-4 text-sm text-text-charcoal">
                    <div className="flex gap-3 items-start p-3.5 rounded-xl border border-white/50 bg-white/40">
                      <span className="material-symbols-outlined text-[#006688] mt-0.5">insights</span>
                      <p className="leading-relaxed text-xs">
                        The model estimates relative weather-impact risk using real weather, road, satellite, and exposure features.
                      </p>
                    </div>
                    <div className="flex gap-3 items-start p-3.5 rounded-xl border border-white/50 bg-white/40">
                      <span className="material-symbols-outlined text-[#8b5000] mt-0.5">psychology</span>
                      <p className="leading-relaxed text-xs">
                        Explainability shows top drivers such as rainfall, built-up density, road density, and elevation.
                      </p>
                    </div>
                    <div className="flex gap-3 items-start p-3.5 rounded-xl border border-amber-200/50 bg-[#ffdcbe]/25">
                      <span className="material-symbols-outlined text-[#ba1a1a] mt-0.5">info</span>
                      <p className="leading-relaxed text-xs font-medium text-text-charcoal">
                        <strong>Honesty Statement:</strong> It supports decision-making, but it is not an official flood forecasting system or official emergency dispatch command.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeModal === 'how-it-works' && (
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-text-charcoal mb-5">How the system works</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { step: 1, label: 'Search / Click Map', desc: 'Search a place or choose a point on the map.' },
                      { step: 2, label: 'Set Start', desc: 'Set it as your start point.' },
                      { step: 3, label: 'Set Destination', desc: 'Choose your destination.' },
                      { step: 4, label: 'Calculate Routes', desc: 'The system calculates live route options.' },
                      { step: 5, label: 'Compare Options', desc: 'It compares risk reduction and ETA tradeoff.' },
                      { step: 6, label: 'Explain Details', desc: 'You can ask why a route or area is risky.' },
                    ].map((item) => (
                      <div key={item.step} className="flex gap-3 p-3 rounded-xl border border-white/50 bg-white/40 items-start">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#006688]/10 text-[#006688] font-bold text-xs shrink-0 mt-0.5">
                          {item.step}
                        </span>
                        <div>
                          <h4 className="font-semibold text-xs text-text-charcoal">{item.label}</h4>
                          <p className="text-[11px] text-text-muted mt-0.5 leading-relaxed">{item.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WelcomePage;
