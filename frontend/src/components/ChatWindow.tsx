"use client";

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatWindowProps {
  quickActions?: string[];
}

export default function ChatWindow({ quickActions = [] }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([{
    role: 'assistant',
    content: "Hi! I'm Anurag's AI representative. I can answer questions about his background, projects, and skills — or help you book an interview with him. What would you like to know?"
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    await sendMessage(input.trim());
  };

  const sendMessage = async (userMsg: string) => {
    setInput('');
    setMessages(prev => [
      ...prev, 
      { role: 'user', content: userMsg },
      { role: 'assistant', content: '' }
    ]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          conversation_history: messages
        }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.token) {
                assistantMsg += data.token;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].content = assistantMsg;
                  return newMsgs;
                });
              }
            } catch (e) {
              console.error("Error parsing JSON chunk", e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => {
        const newMsgs = [...prev];
        if (newMsgs[newMsgs.length - 1]?.role === 'assistant') {
          newMsgs[newMsgs.length - 1].content = "I'm sorry, I'm having trouble connecting right now. Please try again later.";
        } else {
          newMsgs.push({
            role: 'assistant',
            content: "I'm sorry, I'm having trouble connecting right now. Please try again later."
          });
        }
        return newMsgs;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    if (isLoading) return;
    sendMessage(action);
  };

  const showQuickActions = messages.length <= 1 && !isLoading;

  return (
    <div
      id="chat-container"
      className="flex flex-col w-full overflow-hidden"
      style={{
        height: '560px',
        background: '#FFFFFF',
        border: '1px solid #E5E7EB',
        borderRadius: '16px',
        boxShadow: '0 8px 40px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
      }}
    >
      {/* ===== HEADER ===== */}
      <div
        id="chat-header"
        className="flex items-center justify-between px-5 py-3.5"
        style={{
          background: 'linear-gradient(135deg, #0D1B3E 0%, #1A3A6E 100%)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <div className="flex items-center gap-3">
          {/* Avatar */}
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm"
            style={{
              background: 'linear-gradient(135deg, #1A73E8, #00C6FF)',
              boxShadow: '0 2px 8px rgba(26, 115, 232, 0.4)',
            }}
          >
            AS
          </div>
          <div>
            <h2 className="text-white font-semibold text-sm">Anurag&apos;s AI Agent</h2>
            <div className="flex items-center gap-1.5">
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: '#34D399', boxShadow: '0 0 4px rgba(52, 211, 153, 0.6)' }}
              />
              <span className="text-xs" style={{ color: 'rgba(255,255,255,0.55)' }}>Online</span>
            </div>
          </div>
        </div>

        {/* RAG Badge */}
        <div
          className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium"
          style={{
            background: 'rgba(255,255,255,0.1)',
            color: 'rgba(255,255,255,0.65)',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          RAG-Grounded
        </div>
      </div>

      {/* ===== MESSAGES AREA ===== */}
      <div
        id="messages-area"
        className="flex-1 overflow-y-auto px-5 py-4"
        style={{ background: '#FAFBFC' }}
      >
        <div className="space-y-4">
          {messages.map((msg, idx) => {
            if (idx === messages.length - 1 && msg.role === 'assistant' && msg.content === '') {
              return null;
            }
            return (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} ${
                  idx === messages.length - 1 ? (msg.role === 'user' ? 'animate-slide-right' : 'animate-slide-left') : ''
                }`}
              >
                {/* Assistant avatar */}
                {msg.role === 'assistant' && (
                  <div
                    className="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-xs mr-2.5 mt-0.5"
                    style={{
                      background: 'linear-gradient(135deg, #1A73E8, #00C6FF)',
                    }}
                  >
                    AI
                  </div>
                )}

                <div
                  className="max-w-[78%] px-4 py-3"
                  style={
                    msg.role === 'user'
                      ? {
                          background: '#1A73E8',
                          color: '#FFFFFF',
                          borderRadius: '16px 16px 4px 16px',
                          boxShadow: '0 2px 8px rgba(26, 115, 232, 0.2)',
                        }
                      : {
                          background: '#FFFFFF',
                          color: '#1A1A2E',
                          borderRadius: '16px 16px 16px 4px',
                          border: '1px solid #E5E7EB',
                          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
                        }
                  }
                >
                  {msg.role === 'user' ? (
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                  ) : (
                    <div className="chat-prose">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isLoading && messages[messages.length - 1]?.content === '' && (
            <div className="flex justify-start animate-slide-left">
              <div
                className="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-xs mr-2.5"
                style={{ background: 'linear-gradient(135deg, #1A73E8, #00C6FF)' }}
              >
                AI
              </div>
              <div
                className="px-4 py-3.5 flex gap-1.5 items-center"
                style={{
                  background: '#FFFFFF',
                  borderRadius: '16px 16px 16px 4px',
                  border: '1px solid #E5E7EB',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
                }}
              >
                {[0, 1, 2].map(i => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{
                      background: '#1A73E8',
                      animation: `pulse-dot 1.4s infinite ease-in-out`,
                      animationDelay: `${i * 0.16}s`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ===== QUICK ACTIONS ===== */}
        {showQuickActions && quickActions.length > 0 && (
          <div className="mt-5 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <p className="text-xs font-medium mb-2.5" style={{ color: '#9CA3AF', letterSpacing: '0.04em' }}>
              Try asking:
            </p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <button
                  key={action}
                  onClick={() => handleQuickAction(action)}
                  className="px-3.5 py-2 text-xs font-medium transition-all duration-200 cursor-pointer"
                  style={{
                    background: '#FFFFFF',
                    color: '#374151',
                    border: '1px solid #E5E7EB',
                    borderRadius: '999px',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#1A73E8';
                    e.currentTarget.style.color = '#1A73E8';
                    e.currentTarget.style.background = 'rgba(26, 115, 232, 0.04)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(26, 115, 232, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#E5E7EB';
                    e.currentTarget.style.color = '#374151';
                    e.currentTarget.style.background = '#FFFFFF';
                    e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.03)';
                  }}
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ===== INPUT AREA ===== */}
      <div
        id="chat-input"
        className="px-4 py-3"
        style={{
          background: '#FFFFFF',
          borderTop: '1px solid #E5E7EB',
        }}
      >
        <form onSubmit={handleSubmit} className="flex gap-2.5 items-center">
          <input
            ref={inputRef}
            type="text"
            id="message-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Anurag's experience, skills, or book an interview..."
            className="flex-1 text-sm transition-all duration-200 outline-none"
            style={{
              background: '#F5F7FA',
              border: '1px solid #E5E7EB',
              color: '#1A1A2E',
              borderRadius: '12px',
              padding: '10px 16px',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#1A73E8';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(26, 115, 232, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = '#E5E7EB';
              e.currentTarget.style.boxShadow = 'none';
            }}
            disabled={isLoading}
          />
          <button
            type="submit"
            id="send-button"
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center transition-all duration-200 cursor-pointer"
            style={{
              background: !input.trim() || isLoading ? '#D1D5DB' : '#1A73E8',
              color: '#FFFFFF',
              borderRadius: '12px',
              padding: '10px 18px',
              border: 'none',
              boxShadow: !input.trim() || isLoading ? 'none' : '0 2px 8px rgba(26, 115, 232, 0.3)',
              opacity: !input.trim() || isLoading ? 0.6 : 1,
            }}
            onMouseEnter={(e) => {
              if (input.trim() && !isLoading) {
                e.currentTarget.style.background = '#1557B0';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(26, 115, 232, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (input.trim() && !isLoading) {
                e.currentTarget.style.background = '#1A73E8';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(26, 115, 232, 0.3)';
              }
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
