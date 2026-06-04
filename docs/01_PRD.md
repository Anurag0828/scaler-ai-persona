# 📋 Product Requirements Document (PRD)

**Project**: Scaler AI Persona — Autonomous Interview Agent  
**Version**: 1.0  
**Author**: Anurag Sajwan  
**Date**: 2026-05-28  
**Status**: Draft  

---

## 1. Executive Summary

Build an autonomous AI persona that represents Anurag Sajwan in real-time voice calls and text chats. The system must answer questions about background, skills, and experience using **real data** (resume + GitHub repos), handle adversarial probing without hallucinating, and book confirmed interview slots on a real calendar — all with **zero human intervention**.

---

## 2. Problem Statement

Scaler's screening process requires candidates to demonstrate system design, latency engineering, RAG quality, and eval rigor by building a live, end-to-end AI persona. The system must be:
- **Live and callable** at submission time
- **Grounded in real data** (no hardcoded answers)
- **Measurably performant** (latency, accuracy, booking success)

---

## 3. Target Users

| User | Role | Interaction |
|------|------|------------|
| **Scaler Evaluator** | Primary user | Calls phone number, chats on website, probes with adversarial questions |
| **Anurag (Owner)** | System admin | Monitors logs, receives booking confirmations on real calendar |

---

## 4. Product Scope

### 4.1 Part A — Voice Agent (35% weight)

**Description**: A phone number that an evaluator can call. An AI persona picks up and converses naturally.

#### User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|-----------|
| VA-1 | Evaluator | Call a phone number and hear AI introduce itself | I know I'm talking to Anurag's AI representative |
| VA-2 | Evaluator | Ask about Anurag's background and skills | I can assess his fit for the role |
| VA-3 | Evaluator | Interrupt mid-sentence and change topic | I can test if the AI handles barge-in gracefully |
| VA-4 | Evaluator | Ask something the AI doesn't know | I can verify it admits uncertainty honestly |
| VA-5 | Evaluator | Request to book an interview | The AI checks real calendar and books a confirmed slot |
| VA-6 | Anurag | Receive calendar confirmation | I know an interview was booked without my intervention |

#### Acceptance Criteria
- [ ] First response latency < 2 seconds
- [ ] Handles barge-in/interruptions without crashing
- [ ] Answers are grounded in resume/GitHub data (no hallucination)
- [ ] Gracefully says "I don't know" when appropriate
- [ ] Successfully books a real calendar meeting end-to-end
- [ ] No rigid Q&A trees — natural conversation flow

---

### 4.2 Part B — Chat Interface (35% weight)

**Description**: A publicly accessible chat URL where evaluators can text-chat with Anurag's AI persona.

#### User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|-----------|
| CI-1 | Evaluator | Open a public URL and see a chat interface | I can start asking questions immediately |
| CI-2 | Evaluator | Ask "why should we hire Anurag?" | I get a specific, evidence-backed answer |
| CI-3 | Evaluator | Ask about a specific GitHub repo | I get accurate tech stack, purpose, and design tradeoffs |
| CI-4 | Evaluator | Ask about resume details | I get accurate education, experience, and project info |
| CI-5 | Evaluator | Ask to book a call | I can check availability and book directly in chat |
| CI-6 | Evaluator | Try prompt injection or adversarial questions | The AI stays honest, grounded, and in character |
| CI-7 | Evaluator | Ask something only found in a repo README | The AI retrieves and answers correctly (RAG test) |

#### Acceptance Criteria
- [ ] Public URL accessible without login
- [ ] RAG-grounded over real resume and GitHub repos
- [ ] No hardcoded answers — dynamic retrieval
- [ ] Handles prompt injection attempts (stays in character)
- [ ] Zero hallucination on factual questions about Anurag
- [ ] Calendar booking works end-to-end from chat
- [ ] Streaming responses (typing effect)

---

### 4.3 Part C — Evals Report (30% weight)

**Description**: A 1-page PDF documenting system performance metrics.

#### Required Measurements
| Metric | Category |
|--------|----------|
| First-response latency | Voice quality |
| Transcription accuracy | Voice quality |
| Task completion rate (booking success) | Voice quality |
| Hallucination rate | Chat groundedness |
| Retrieval precision/recall | Chat groundedness |
| 3 failure modes + root causes + fixes | Reliability |
| 1 conscious tradeoff with rationale | Design decisions |
| What you'd build with 2 more weeks | Vision |

---

## 5. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Voice first-response latency | < 2 seconds | Timestamp diff (call connect → first AI word) |
| Booking success rate | > 80% across test calls | N successful bookings / N booking attempts |
| Hallucination rate | < 5% | Judge model + golden Q&A set comparison |
| RAG retrieval precision | > 85% | Manual review of top-K chunks vs. query |
| Chat response time | < 3 seconds (first token) | Client-side timing |
| System uptime | 99%+ for 7 days post-submission | Health check monitoring |

---

## 6. Out of Scope

- UI polish (explicitly stated by Scaler as not evaluated)
- Multi-language support
- User authentication / login
- Mobile app
- Payment processing

---

## 7. Constraints

| Constraint | Detail |
|-----------|--------|
| Budget | ₹0 — all free tiers only |
| Timeline | Must be live at submission, stay live 7 days |
| Tech stack | NVIDIA NIM (LLM), Vapi (voice), Pinecone (vector DB), Cal.com (calendar), Vercel (hosting) |
| Data sources | Real resume + real public GitHub repos only |

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Vapi free credits run out | Voice agent goes offline | Medium | Monitor usage, limit test calls |
| NVIDIA NIM rate limits hit | Slow responses | Low | Cache frequent queries, implement retry logic |
| Pinecone cold starts | Slow RAG retrieval | Low | Keep index warm with periodic pings |
| Render cold starts (backend) | Slow webhook responses to Vapi | High | Use keep-alive pings every 10 min |
| Cal.com API changes | Booking breaks | Low | Pin API version, add error handling |
| Prompt injection succeeds | AI breaks character | Medium | System prompt hardening, input sanitization |

---

## 9. Dependencies

```
Resume (PDF/text) ──────┐
                        ├──▶ Data Ingestion Pipeline ──▶ Pinecone Vector DB
GitHub Repos ───────────┘
                                                              │
                    ┌─────────────────────────────────────────┘
                    ▼
              RAG Backend (FastAPI)
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Vapi      Next.js    Cal.com
     (Voice)     (Chat)    (Calendar)
```

---

## 10. Deliverables Checklist

- [ ] Live phone number (voice agent)
- [ ] Public chat URL
- [ ] GitHub repo with clean README + architecture diagram
- [ ] Setup instructions in README
- [ ] Cost breakdown (per call / per chat session)
- [ ] 1-page eval report PDF
- [ ] Loom walkthrough video (≤ 4 min)
- [ ] Submission form filled
