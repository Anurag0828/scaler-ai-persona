# 🗺️ Project Plan & Roadmap

**Project**: Scaler AI Persona  
**Estimated Total Time**: 12-16 hours  
**Date**: 2026-05-28  

---

## 1. Project Structure

```
Scaler_AI_Agent/
│
├── docs/                          # 📋 Documentation (you are here)
│   ├── 01_PRD.md                  # Product Requirements Document
│   ├── 02_ARCHITECTURE.md         # System Architecture
│   ├── 03_SRS.md                  # Software Requirements Spec
│   ├── 04_WORKFLOWS.md            # Workflow Diagrams
│   ├── 05_API_SPEC.md             # API Specification
│   ├── 06_PROJECT_PLAN.md         # This file
│   └── 07_COST_ANALYSIS.md        # Cost Breakdown
│
├── scripts/                       # 🔧 Data ingestion scripts
│   ├── ingest_resume.py           # Parse & embed resume
│   ├── ingest_github.py           # Crawl & embed GitHub repos
│   └── requirements.txt           # Script dependencies
│
├── backend/                       # ⚙️ FastAPI backend
│   ├── main.py                    # FastAPI app + routes
│   ├── rag_engine.py              # Pinecone search + NIM generation
│   ├── calendar_service.py        # Cal.com API integration
│   ├── vapi_handler.py            # Vapi webhook handler
│   ├── prompts.py                 # System prompts
│   ├── config.py                  # Environment config
│   ├── requirements.txt           # Backend dependencies
│   ├── Dockerfile                 # Container for Render
│   └── render.yaml                # Render deployment config
│
├── frontend/                      # 💬 Next.js chat interface
│   ├── app/
│   │   ├── page.tsx               # Main chat page
│   │   ├── layout.tsx             # Root layout
│   │   ├── globals.css            # Global styles
│   │   └── api/
│   │       └── chat/route.ts      # API proxy to backend
│   ├── components/
│   │   ├── ChatWindow.tsx         # Chat UI component
│   │   ├── MessageBubble.tsx      # Individual message
│   │   └── BookingWidget.tsx      # Calendar booking UI
│   ├── package.json
│   └── vercel.json                # Vercel config
│
├── eval/                          # 📊 Evaluation scripts
│   ├── test_voice.py              # Voice agent test runner
│   ├── test_chat.py               # Chat groundedness tests
│   ├── golden_qa.json             # Golden Q&A set for eval
│   └── generate_report.py         # Generate eval PDF
│
├── vapi/                          # 📞 Vapi configuration
│   └── assistant_config.json      # Vapi assistant settings
│
├── data/                          # 📄 Source data
│   ├── resume.pdf                 # Your resume
│   ├── resume.txt                 # Resume as plain text
│   └── talking_points.md          # Key selling points
│
├── memory.md                      # 🧠 Chat memory log
├── README.md                      # 📖 Project README
├── .env.example                   # 🔑 Environment variables template
└── .gitignore                     # Git ignore rules
```

---

## 2. Development Phases

### Phase 1: Foundation (2-3 hours)
| Task | Time | Status |
|------|------|--------|
| Create project structure | 15 min | ⬜ |
| Set up `.env` with all API keys | 15 min | ⬜ |
| Write resume as plain text | 30 min | ⬜ |
| Write talking points document | 30 min | ⬜ |
| Set up Cal.com account + event type | 30 min | ⬜ |
| Create Pinecone index | 15 min | ⬜ |

### Phase 2: Data Ingestion (2-3 hours)
| Task | Time | Status |
|------|------|--------|
| Build resume ingestion script | 45 min | ⬜ |
| Build GitHub crawler script | 60 min | ⬜ |
| Test chunking + embedding pipeline | 30 min | ⬜ |
| Verify vectors in Pinecone dashboard | 15 min | ⬜ |

### Phase 3: Backend API (3-4 hours)
| Task | Time | Status |
|------|------|--------|
| Set up FastAPI project | 15 min | ⬜ |
| Build RAG engine (search + generate) | 60 min | ⬜ |
| Build calendar service (availability + booking) | 60 min | ⬜ |
| Build Vapi webhook handler | 45 min | ⬜ |
| Build chat endpoint with streaming | 45 min | ⬜ |
| Deploy to Render | 30 min | ⬜ |

### Phase 4: Voice Agent (1-2 hours)
| Task | Time | Status |
|------|------|--------|
| Create Vapi assistant with system prompt | 30 min | ⬜ |
| Configure tool functions (search, availability, book) | 30 min | ⬜ |
| Get free phone number | 5 min | ⬜ |
| Test end-to-end voice flow | 30 min | ⬜ |

### Phase 5: Chat Frontend (2-3 hours)
| Task | Time | Status |
|------|------|--------|
| Initialize Next.js project | 15 min | ⬜ |
| Build chat UI component | 60 min | ⬜ |
| Implement streaming response display | 30 min | ⬜ |
| Build booking widget | 30 min | ⬜ |
| Deploy to Vercel | 15 min | ⬜ |

### Phase 6: Testing & Evals (2-3 hours)
| Task | Time | Status |
|------|------|--------|
| Create golden Q&A set (20+ questions) | 30 min | ⬜ |
| Test voice agent (10+ calls) | 30 min | ⬜ |
| Test chat (20+ conversations) | 30 min | ⬜ |
| Test adversarial prompts | 20 min | ⬜ |
| Measure latency metrics | 15 min | ⬜ |
| Generate eval PDF report | 30 min | ⬜ |

### Phase 7: Polish & Submit (1 hour)
| Task | Time | Status |
|------|------|--------|
| Write README with architecture diagram | 30 min | ⬜ |
| Record Loom walkthrough (≤4 min) | 15 min | ⬜ |
| Fill submission form | 10 min | ⬜ |
| Final smoke test (call + chat) | 15 min | ⬜ |

---

## 3. Environment Variables Required

```env
# NVIDIA NIM
NVIDIA_API_KEY=nvapi-xxxx

# Pinecone
PINECONE_API_KEY=pcsk_xxxx
PINECONE_INDEX_NAME=scaler-persona

# Cal.com
CAL_API_KEY=cal_xxxx
CAL_EVENT_TYPE_ID=123456

# Vapi
VAPI_API_KEY=vapi_xxxx
VAPI_PHONE_NUMBER_ID=xxxx

# GitHub (optional, for higher rate limits)
GITHUB_TOKEN=ghp_xxxx
GITHUB_USERNAME=your-username

# App
BACKEND_URL=https://your-app.onrender.com
FRONTEND_URL=https://your-app.vercel.app
```

---

## 4. Dependencies

### Backend (`backend/requirements.txt`)
```
fastapi==0.115.0
uvicorn==0.30.0
openai==1.40.0          # NVIDIA NIM is OpenAI-compatible
pinecone-client==5.0.0
langchain==0.3.0
langchain-text-splitters==0.3.0
httpx==0.27.0            # For Cal.com API calls
python-dotenv==1.0.0
PyPDF2==3.0.1
sse-starlette==2.1.0     # For streaming responses
```

### Frontend (`frontend/package.json`)
```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-markdown": "^9.0.0"
  }
}
```

---

## 5. Risk Mitigation Checklist

- [ ] Render cold start → Add keep-alive ping (cron job every 10 min)
- [ ] NVIDIA NIM credits running low → Monitor usage, have Gemini as fallback
- [ ] Vapi credits running low → Limit test calls, monitor dashboard
- [ ] Pinecone query slow → Use serverless, keep index small
- [ ] Prompt injection → Harden system prompt, test adversarial inputs
- [ ] Cal.com API rate limit → Cache availability for 5 min
