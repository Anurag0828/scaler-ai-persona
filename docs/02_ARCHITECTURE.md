# 🏗️ System Architecture Document

**Project**: Scaler AI Persona  
**Version**: 1.0  
**Date**: 2026-05-28  

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│                                                          │
│   ┌─────────────────┐       ┌─────────────────────┐     │
│   │ 📞 Voice Agent   │       │ 💬 Chat Interface    │     │
│   │ (Vapi Platform)  │       │ (Next.js / Vercel)  │     │
│   │ Free US Number   │       │ Public URL           │     │
│   └───────┬─────────┘       └──────────┬──────────┘     │
└───────────┼────────────────────────────┼────────────────┘
            │ Webhook POST               │ REST API
            ▼                            ▼
┌──────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                         │
│                 (FastAPI on Render)                       │
│                                                          │
│   /vapi-webhook  /chat  /availability  /book  /health    │
│         │          │         │           │               │
│         ▼          ▼         ▼           ▼               │
│   ┌──────────┐ ┌──────┐ ┌────────┐ ┌────────┐           │
│   │Vapi Tool │ │ RAG  │ │Cal.com │ │Cal.com │           │
│   │Handler   │ │Engine│ │Slots   │ │Booking │           │
│   └──────────┘ └──────┘ └────────┘ └────────┘           │
└──────────────────────────────────────────────────────────┘
            │          │         │           │
            ▼          ▼         ▼           ▼
┌──────────────────────────────────────────────────────────┐
│                  INTELLIGENCE LAYER                      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ 🧠 NVIDIA NIM │  │ 🔍 Pinecone   │  │ 📅 Cal.com   │   │
│  │ LLM + Embed  │  │ Vector DB    │  │ Calendar API │   │
│  │ 1000 credits │  │ Free 2GB     │  │ Free tier    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
            ▲ (one-time ingestion)
┌──────────────────────────────────────────────────────────┐
│                     DATA LAYER                           │
│                                                          │
│   Resume (PDF) + GitHub Repos → Chunk → Embed → Upsert  │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### 2.1 Data Ingestion (`scripts/`)
- **Resume Parser**: PyPDF2 → extract text
- **GitHub Crawler**: REST API → fetch repos, READMEs, languages, commits
- **Chunker**: LangChain RecursiveCharacterTextSplitter (500 chars, 100 overlap)
- **Embedder**: NVIDIA NIM embedding model → 1024-dim vectors
- **Store**: Upsert to Pinecone with metadata (source, section, repo_name)

### 2.2 Backend API (`backend/`)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/vapi-webhook` | POST | Receive Vapi tool calls (search, availability, book) |
| `/chat` | POST | RAG-powered chat (Pinecone search → NIM → stream) |
| `/availability` | GET | Proxy to Cal.com `/v2/slots` |
| `/book` | POST | Proxy to Cal.com `/v2/bookings` |
| `/health` | GET | Uptime monitoring |

### 2.3 Voice Agent (Vapi)
- Free US phone number from Vapi dashboard
- STT: Deepgram (included in Vapi credits)
- LLM: NVIDIA NIM via custom LLM config or Vapi's server URL
- TTS: Vapi default or ElevenLabs free tier
- Tools: `check_availability`, `book_meeting`, `search_knowledge`

### 2.4 Chat Frontend (`frontend/`)
- Next.js App Router on Vercel
- Streaming SSE responses
- Markdown rendering for rich answers
- Inline calendar booking UI

---

## 3. Deployment Map

| Component | Platform | URL Pattern | Cost |
|-----------|----------|-------------|------|
| Frontend | Vercel | `*.vercel.app` | Free |
| Backend | Render | `*.onrender.com` | Free |
| Voice | Vapi Cloud | Phone number | Free ($10 trial) |
| Vector DB | Pinecone | Serverless | Free |
| Calendar | Cal.com | API | Free |
| LLM | NVIDIA NIM | API | Free (1000 credits) |

---

## 4. Security

- Vapi webhook: validate secret header
- CORS: whitelist Vercel domain only
- API keys: environment variables only
- Prompt injection: system prompt hardening + input sanitization
- Rate limiting: 10 req/min per IP on chat
