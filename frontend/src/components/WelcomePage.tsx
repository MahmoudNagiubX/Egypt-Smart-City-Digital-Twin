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
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="flex-1 w-full max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center z-10 min-h-0 py-4"
      >
        <style dangerouslySetInnerHTML={{__html: `
          @keyframes pulse {
            0%, 100% { opacity: 0.15; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(1.1); }
          }
        `}} />

        {/* Column 1 (Left column, spanning 7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-start text-left gap-4">
          <h1
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 'clamp(28px, 3.5vw, 44px)',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              lineHeight: 1.15,
              color: 'var(--stitch-text-charcoal)',
            }}
          >
            Stay ahead with a<br />
            <span className="stitch-marker-highlight">safer</span> city route plan
          </h1>
          
          <p
            style={{ 
              fontSize: 'clamp(13px, 1.2vw, 15px)', 
              color: 'var(--stitch-text-muted)', 
              lineHeight: 1.5,
              maxWidth: '480px' 
            }}
          >
            Visualize weather risk, traffic pressure, and weather-aware emergency routes across Nasr City in real-time.
          </p>

          <div className="flex flex-row items-center gap-4 mt-2">
            <button
              id="welcome-open-dashboard"
              onClick={onOpenDashboard}
              className="font-semibold shadow-sm transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0"
              style={{
                background: '#1A1C1E',
                color: 'white',
                padding: '10px 24px',
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
              className="font-semibold shadow-sm transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0"
              style={{
                background: 'white',
                color: '#1A1C1E',
                padding: '10px 24px',
                borderRadius: 10,
                fontSize: 13,
                border: '1px solid #bcc8d1',
                cursor: 'pointer',
              }}
              onMouseOver={e => ((e.currentTarget as HTMLButtonElement).style.background = '#f5faff')}
              onMouseOut={e => ((e.currentTarget as HTMLButtonElement).style.background = 'white')}
            >
              See how it works
            </button>
          </div>

          {/* 4 Compact Feature/Value Cards in a 2x2 grid */}
          <div className="grid grid-cols-2 gap-3 w-full max-w-[500px] mt-4">
            {[
              { emoji: '🌧️', title: 'Live Rain Risk', desc: 'Real-time ML risk scores per zone' },
              { emoji: '🛣️', title: 'Safer Routing', desc: 'Evade high-risk flooding spots' },
              { emoji: '🔍', title: 'Explainable AI', desc: 'Understand the underlying causes' },
              { emoji: '📍', title: 'Smart Search', desc: 'Search streets, landmarks, POIs' },
            ].map((feat) => (
              <div 
                key={feat.title} 
                className="stitch-card p-3 flex flex-col gap-1 border border-white/50 bg-white/40 shadow-xs rounded-xl hover:bg-white/60 transition-colors"
                style={{ padding: '0.75rem 1rem' }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-base">{feat.emoji}</span>
                  <h3 className="font-bold text-xs text-text-charcoal m-0">{feat.title}</h3>
                </div>
                <p className="text-[10px] text-text-muted m-0 leading-normal">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2 (Right column, spanning 5 cols) */}
        <div className="lg:col-span-5 w-full flex justify-center h-full max-h-[380px] lg:max-h-full items-center">
          <div 
            className="stitch-card w-full max-w-[380px] aspect-[1.1] relative shadow-lg overflow-hidden border border-white/60 flex flex-col"
            style={{ borderRadius: 24, padding: 0 }}
          >
            {/* Header / Search bar of the mini-map */}
            <div className="flex items-center gap-2 px-3 py-2 border-b border-white/50 bg-white/40 z-10 shrink-0">
              <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
              <div className="flex-1 bg-white/60 border border-white/80 rounded-md py-1 px-2 text-[9px] text-text-muted flex items-center gap-1.5 font-sans truncate shadow-xs">
                <span className="material-symbols-outlined text-[10px]">search</span>
                <span>Nasr City, Cairo (Emergency)</span>
              </div>
            </div>

            {/* Simulated Live Map Canvas */}
            <div className="flex-1 bg-[#e8f1f8] relative overflow-hidden">
              {/* Street grid representation (SVG background) */}
              <svg width="100%" height="100%" className="absolute inset-0 opacity-20 pointer-events-none" style={{ stroke: '#006688', strokeWidth: 0.75 }}>
                {/* Horizontal streets */}
                <line x1="0" y1="20%" x2="100%" y2="20%" />
                <line x1="0" y1="50%" x2="100%" y2="40%" />
                <line x1="0" y1="75%" x2="100%" y2="85%" />
                {/* Vertical/slanted streets */}
                <line x1="20%" y1="0" x2="10%" y2="100%" />
                <line x1="45%" y1="0" x2="55%" y2="100%" />
                <line x1="80%" y1="0" x2="70%" y2="100%" />
                {/* Diagonal secondary roads */}
                <line x1="0" y1="90%" x2="90%" y2="0" strokeDasharray="3 3" />
                <line x1="10%" y1="10%" x2="100%" y2="70%" strokeDasharray="2 2" />
              </svg>

              {/* Weather risk intensity zones (blobs) */}
              <div 
                className="absolute rounded-full" 
                style={{ 
                  top: '15%', 
                  left: '35%', 
                  width: '90px', 
                  height: '90px', 
                  background: 'radial-gradient(circle, rgba(186,26,26,0.22) 0%, rgba(186,26,26,0) 70%)', 
                  filter: 'blur(4px)',
                  animation: 'pulse 3s infinite ease-in-out'
                }} 
              />
              <div 
                className="absolute rounded-full" 
                style={{ 
                  top: '60%', 
                  left: '60%', 
                  width: '110px', 
                  height: '110px', 
                  background: 'radial-gradient(circle, rgba(255,122,0,0.18) 0%, rgba(255,122,0,0) 70%)', 
                  filter: 'blur(4px)' 
                }} 
              />

              {/* Safe Route line (SVG Path with dash-array animation) */}
              <svg width="100%" height="100%" className="absolute inset-0">
                {/* Safe route (green/blue) */}
                <path 
                  d="M 60,240 C 90,180 180,180 200,120 S 290,140 330,70" 
                  fill="none" 
                  stroke="#006d36" 
                  strokeWidth="3.5" 
                  strokeLinecap="round" 
                  style={{
                    strokeDasharray: '400',
                    strokeDashoffset: '0',
                    filter: 'drop-shadow(0px 1.5px 3px rgba(0,109,54,0.4))'
                  }}
                />
                {/* Normal dangerous route (red dotted) */}
                <path 
                  d="M 60,240 C 130,220 120,70 200,120 S 270,40 330,70" 
                  fill="none" 
                  stroke="#ba1a1a" 
                  strokeWidth="2" 
                  strokeDasharray="4 4" 
                  opacity="0.85" 
                  strokeLinecap="round" 
                />
              </svg>

              {/* Start marker (A) */}
              <div 
                className="absolute flex items-center justify-center bg-[#006688] text-white rounded-full shadow-md font-bold text-[9px] cursor-default transition-transform hover:scale-110"
                style={{ top: '228px', left: '48px', width: '22px', height: '22px', border: '1.5px solid white' }}
              >
                A
              </div>

              {/* Destination marker (B) */}
              <div 
                className="absolute flex items-center justify-center bg-[#006d36] text-white rounded-full shadow-md font-bold text-[9px] cursor-default transition-transform hover:scale-110"
                style={{ top: '58px', left: '318px', width: '22px', height: '22px', border: '1.5px solid white' }}
              >
                B
              </div>

              {/* POI Markers: Hospital, Emergency */}
              <div 
                className="absolute bg-white text-[#ba1a1a] rounded-lg shadow-sm border border-white/50 flex items-center justify-center text-[11px] p-1 cursor-default hover:-translate-y-0.5 transition-transform"
                style={{ top: '150px', left: '160px', width: '20px', height: '20px' }}
                title="Emergency Center"
              >
                🏥
              </div>
              <div 
                className="absolute bg-white text-[#006688] rounded-lg shadow-sm border border-white/50 flex items-center justify-center text-[11px] p-1 cursor-default hover:-translate-y-0.5 transition-transform"
                style={{ top: '90px', left: '260px', width: '20px', height: '20px' }}
                title="Police Station"
              >
                👮
              </div>

              {/* Live HUD card overlay */}
              <div 
                className="absolute bottom-3 left-3 right-3 stitch-glass rounded-xl p-2.5 border border-white/60 flex items-center justify-between shadow-md"
                style={{ background: 'rgba(255,255,255,0.85)' }}
              >
                <div className="flex flex-col">
                  <span className="text-[7.5px] text-text-muted font-bold uppercase tracking-wider">Live Route Recommendation</span>
                  <span className="text-[10px] font-bold text-text-charcoal mt-0.5">Use Emergency Route (Route B)</span>
                </div>
                <div className="flex items-center gap-1 bg-[#83fba5]/40 text-[#006d36] text-[8.5px] font-bold px-2 py-0.5 rounded-full border border-[#83fba5]/60">
                  <span>92% Safer</span>
                </div>
              </div>
            </div>
          </div>
        </div>
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
