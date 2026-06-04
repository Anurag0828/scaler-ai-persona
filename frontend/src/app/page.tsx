import ChatWindow from '@/components/ChatWindow';

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4 md:p-8 font-sans selection:bg-blue-500/30">
      
      {/* Background aesthetic */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-900/20 blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-900/20 blur-[120px]"></div>
      </div>

      <div className="z-10 w-full max-w-4xl mx-auto flex flex-col items-center">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 tracking-tight mb-4">
            Meet Anurag's AI Persona
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
            I'm an autonomous agent powered by NVIDIA NIM & RAG. Ask me anything about Anurag's engineering background or check his availability to schedule an interview.
          </p>
        </div>

        <ChatWindow />
        
        <div className="mt-8 text-center text-gray-500 text-sm">
          Built for the Scaler AI Engineer Screening Assignment • 2024
        </div>
      </div>
    </main>
  );
}
