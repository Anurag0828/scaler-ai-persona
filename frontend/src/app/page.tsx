import ChatWindow from '@/components/ChatWindow';

const techStack = [
  { name: 'NVIDIA NIM', icon: '🧠' },
  { name: 'Pinecone', icon: '🔍' },
  { name: 'Cal.com', icon: '📅' },
  { name: 'Vapi', icon: '📞' },
];

const quickActions = [
  "What's Anurag's experience?",
  "Tell me about his projects",
  "What AI tools does he use?",
  "Book an interview",
];

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(180deg, #F5F7FA 0%, #FFFFFF 40%, #F0F4FF 100%)' }}>

      {/* ===== TOP NAV BAR ===== */}
      <nav
        id="main-nav"
        className="w-full border-b"
        style={{
          background: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderColor: '#E5E7EB',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Logo / Brand */}
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
              style={{ background: 'linear-gradient(135deg, #1A73E8, #00C6FF)' }}
            >
              AS
            </div>
            <div>
              <span className="font-bold text-sm tracking-wide" style={{ color: '#0D1B3E' }}>
                SCALER AI PERSONA
              </span>
            </div>
          </div>

          {/* Right badge */}
          <div
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
            style={{
              background: 'rgba(26, 115, 232, 0.08)',
              color: '#1A73E8',
              border: '1px solid rgba(26, 115, 232, 0.15)',
            }}
          >
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Powered by NVIDIA NIM
          </div>
        </div>
      </nav>

      {/* ===== HERO SECTION ===== */}
      <div className="w-full pt-10 pb-6 sm:pt-14 sm:pb-8 relative overflow-hidden">
        {/* Subtle glow effect */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at 50% 0%, rgba(26, 115, 232, 0.08) 0%, transparent 60%)',
          }}
        />

        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center relative z-10">
          <div className="animate-fade-in-up">
            {/* Eyebrow */}
            <p
              className="text-xs font-semibold tracking-widest uppercase mb-4"
              style={{ color: '#1A73E8', letterSpacing: '0.15em' }}
            >
              AUTONOMOUS AI AGENT
            </p>

            {/* Headline */}
            <h1
              className="text-3xl sm:text-4xl md:text-5xl font-extrabold leading-tight mb-5 tracking-tight"
              style={{ color: '#0D1B3E' }}
            >
              Meet{' '}
              <span className="gradient-text">Anurag&apos;s AI</span>{' '}
              Persona
            </h1>

            {/* Subtitle */}
            <p
              className="text-base sm:text-lg max-w-2xl mx-auto leading-relaxed mb-8"
              style={{ color: '#6B7280' }}
            >
              RAG-grounded agent that answers questions about Anurag&apos;s engineering background, projects, and skills — or autonomously books an interview on his calendar.
            </p>
          </div>

          {/* Tech Stack Badges */}
          <div className="flex flex-wrap justify-center gap-2.5 mb-8 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
            {techStack.map((tech) => (
              <div
                key={tech.name}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-medium transition-all duration-200 cursor-default"
                style={{
                  background: '#FFFFFF',
                  color: '#374151',
                  border: '1px solid #E5E7EB',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#1A73E8';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(26, 115, 232, 0.12)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#E5E7EB';
                  e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)';
                }}
              >
                <span>{tech.icon}</span>
                <span>{tech.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ===== CHAT SECTION ===== */}
      <div className="flex-1 w-full max-w-3xl mx-auto px-4 sm:px-6 pb-6 animate-fade-in-up" style={{ animationDelay: '0.25s' }}>
        <ChatWindow quickActions={quickActions} />
      </div>


    </main>
  );
}
