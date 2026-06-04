# 🧠 MEMORY.MD — Project Chat Memory

> **INSTRUCTION TO AI AGENT**: Record EVERY chat query, decision, and outcome in this file. Every time the user asks something or a decision is made, append it below under the correct section. This file is the single source of truth for the entire project's conversation history. Never skip logging. Always update this file before ending a response.

---

## 📋 Project: Scaler AI Engineer Screening Assignment

**Goal**: Build an AI persona of Anurag Sajwan that can be called (voice), chatted with (web), and used to book an interview — fully automated, no human in the loop.

---

## 💬 Chat History Log

### Chat 1 — Project Understanding (2026-05-28 19:14 IST)
- **User Query**: Shared the full Scaler AI Engineer Screening Assignment requirements
- **What We Discussed**: 
  - Part A: Voice Agent (phone call AI) — 35%
  - Part B: Chat Interface (website chatbot) — 35%
  - Part C: Evals Report (PDF) — 30%
- **Outcome**: User needed explanation of the project

### Chat 2 — Simple Explanation (2026-05-28 19:17 IST)
- **User Query**: "give me explanation about what i am building because i am confused"
- **What We Discussed**:
  - Explained the project in simple terms — building a robot clone of yourself
  - Voice Agent = AI picks up phone calls
  - Chat Interface = AI answers on a website
  - Eval Report = test report card for your AI
- **Outcome**: User understood but had cost concerns

### Chat 3 — Free Services (2026-05-28 19:20 IST)
- **User Query**: "i want free ones not paid ones, for what i need vapi openai and deepgram?"
- **What We Discussed**:
  - Vapi = phone company (manages calls, gives free number)
  - Deepgram = ears (converts speech to text)
  - OpenAI = brain (thinks and generates answers)
  - Proposed replacing OpenAI with Google Gemini (completely free)
- **Outcome**: User asked about NVIDIA as alternative

### Chat 4 — NVIDIA NIM Decision (2026-05-28 19:21 IST)
- **User Query**: "or i can use nvidia ai models"
- **What We Discussed**:
  - NVIDIA NIM gives 1,000 free credits, no card, no expiry
  - OpenAI-compatible API (drop-in replacement)
  - Access to Llama, Mistral, DeepSeek models
- **Outcome**: NVIDIA NIM chosen as AI brain (replaces OpenAI)

### Chat 5 — Memory File Created (2026-05-28 19:22 IST)
- **User Query**: "make this chats memory.md file in this dir"
- **Outcome**: Created this memory.md file

---

## ✅ Decisions Made

| # | Decision | Chosen | Why |
|---|----------|--------|-----|
| 1 | AI Brain (LLM) | **NVIDIA NIM** | Free 1,000 credits, no card, OpenAI-compatible |
| 2 | Voice Platform | **Vapi** | Free phone number + $10 trial credits |
| 3 | Vector Database | **Pinecone** | Free tier (2GB), works with LangChain |
| 4 | Calendar Booking | **Cal.com** | Free, has API for availability + booking |
| 5 | Chat Website Host | **Vercel** | Free, deploys Next.js easily |

---

## 🔧 Final Tech Stack (₹0 Cost)

| Service | Purpose | Cost |
|---------|---------|------|
| Vapi | Phone number + voice calls | Free ($10 trial) |
| NVIDIA NIM | AI brain (LLM) | Free (1,000 credits) |
| Pinecone | Vector DB for RAG | Free |
| Cal.com | Calendar + booking | Free |
| Vercel | Hosts chat website | Free |

---

### Chat 6 — Project Documentation (2026-05-28 19:25 IST)
- **User Query**: "create the documents for the project... a blueprint a workflow diagram... like src document and all, keep in docs folder"
- **What We Created**:
  - `docs/01_PRD.md` — Product Requirements Document (user stories, acceptance criteria, success metrics)
  - `docs/02_ARCHITECTURE.md` — System architecture with ASCII diagrams (4-layer design)
  - `docs/03_SRS.md` — Software Requirements Specification (functional + non-functional reqs)
  - `docs/04_WORKFLOWS.md` — Workflow diagrams (voice call, chat, booking, ingestion, error handling)
  - `docs/05_API_SPEC.md` — API specification (all endpoints with request/response schemas)
  - `docs/06_PROJECT_PLAN.md` — Project plan (directory structure, phases, timeline, dependencies)
  - `docs/07_COST_ANALYSIS.md` — Cost breakdown (₹0 total, per-call/per-session estimates)
- **Outcome**: Full production-grade documentation suite created

### Chat 7 — Missing Documents Created (2026-06-04 20:37 IST)
- **User Query**: "built the remaining documents so you can make it accordingly"
- **What We Created**:
  - `docs/08_SYSTEM_PROMPTS.md` — Voice + Chat system prompts, persona rules, prompt injection defenses, tone guide
  - `docs/09_GOLDEN_QA.md` — 30-question golden Q&A set for eval (answers TBD after data ingestion)
  - `docs/10_VAPI_CONFIG.md` — Full Vapi assistant JSON, tool definitions, voice/transcriber settings, latency optimization
- **Outcome**: Full documentation suite (10 docs) now complete. Ready to build once user provides resume + GitHub + API keys.

---

## ⏳ Still Needed From User

- [ ] Resume (text or file path)
- [ ] GitHub username
- [ ] API keys (NVIDIA, Vapi, Pinecone, Cal.com, Vercel)
- [ ] Key talking points for "why hire Anurag"

---

## 🚧 Build Progress

- [x] Step 0: Documentation (10/10 docs complete)
- [ ] Step 1: Data preparation (resume + GitHub ingestion)
- [ ] Step 2: Backend API (FastAPI + RAG + Cal.com)
- [ ] Step 3: Voice Agent (Vapi setup)
- [ ] Step 4: Chat Website (Next.js + Vercel)
- [ ] Step 5: Testing + Eval Report (PDF)
