# 🔄 Workflow Diagrams

**Project**: Scaler AI Persona  
**Version**: 1.0  
**Date**: 2026-05-28  

---

## 1. Voice Call — Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE CALL WORKFLOW                          │
└─────────────────────────────────────────────────────────────────┘

  Evaluator                  Vapi                    FastAPI
     │                        │                        │
     │──── Dials phone ──────▶│                        │
     │                        │                        │
     │◀── "Hi! I'm Anurag's  │                        │
     │     AI assistant..."  ─┤                        │
     │                        │                        │
     │── "What's his          │                        │
     │    experience?" ──────▶│                        │
     │                        │── tool: search ───────▶│
     │                        │    knowledge           │──▶ Pinecone
     │                        │                        │◀── chunks
     │                        │                        │──▶ NVIDIA NIM
     │                        │◀── answer ────────────│◀── response
     │◀── "Anurag has..."  ──┤                        │
     │                        │                        │
     │── "Can we schedule     │                        │
     │    an interview?" ────▶│                        │
     │                        │── tool: check ────────▶│
     │                        │    availability        │──▶ Cal.com
     │                        │◀── slots ─────────────│◀── slots
     │◀── "I have openings   │                        │
     │     at 10AM, 2PM..." ─┤                        │
     │                        │                        │
     │── "2PM works" ────────▶│                        │
     │                        │── tool: book ─────────▶│
     │                        │    meeting             │──▶ Cal.com
     │                        │◀── confirmation ──────│◀── booked
     │◀── "Done! Meeting     │                        │
     │     booked at 2PM"  ──┤                        │
     │                        │                        │
     │── "Thanks, bye" ─────▶│                        │
     │◀── "Goodbye!" ────────┤                        │
     │                        │                        │
```

---

## 2. Chat Message — Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHAT MESSAGE WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

  Browser          Next.js (Vercel)        FastAPI (Render)
     │                   │                       │
     │── Type message ──▶│                       │
     │                   │── POST /chat ────────▶│
     │                   │   {message, history}   │
     │                   │                       │
     │                   │                       │──▶ Embed query
     │                   │                       │     (NVIDIA NIM)
     │                   │                       │
     │                   │                       │──▶ Search Pinecone
     │                   │                       │     (top-5 chunks)
     │                   │                       │
     │                   │                       │──▶ Build prompt:
     │                   │                       │     System + Context
     │                   │                       │     + User message
     │                   │                       │
     │                   │                       │──▶ NVIDIA NIM
     │                   │                       │     (stream)
     │                   │                       │
     │                   │◀── SSE stream ───────│
     │◀── Show typing   │   token by token       │
     │    effect ────────┤                       │
     │                   │                       │
     │  [Message done]   │                       │
```

---

## 3. Calendar Booking — Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  CALENDAR BOOKING WORKFLOW                      │
└─────────────────────────────────────────────────────────────────┘

  User/Agent              FastAPI                Cal.com
     │                       │                      │
     │── "Check June 2" ───▶│                      │
     │                       │── GET /v2/slots ────▶│
     │                       │   ?start=...         │──▶ Google
     │                       │   &end=...           │     Calendar
     │                       │                      │◀── busy/free
     │                       │◀── available slots ──│
     │◀── "10AM, 2PM, 4PM" ─│                      │
     │                       │                      │
     │── "Book 2PM" ────────▶│                      │
     │                       │── POST /v2/bookings ▶│
     │                       │   {start, name,      │──▶ Google
     │                       │    email, eventType}  │     Calendar
     │                       │                      │◀── confirmed
     │                       │◀── booking details ──│
     │◀── "Confirmed!       │                      │
     │     Meeting at 2PM"  ─│                      │
     │                       │                      │
     │   📧 Anurag gets email confirmation          │
```

---

## 4. Data Ingestion — One-Time Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  DATA INGESTION WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

  Step 1: Collect Data
  ═══════════════════
  Resume (PDF)  ──▶  PyPDF2  ──▶  Raw Text
  GitHub API    ──▶  requests ──▶  READMEs + Repo Metadata

  Step 2: Process
  ═══════════════
  Raw Text  ──▶  LangChain TextSplitter  ──▶  Chunks (500 chars)
                 (100 char overlap)

  Step 3: Embed
  ═════════════
  Chunks  ──▶  NVIDIA NIM Embed API  ──▶  1024-dim Vectors

  Step 4: Store
  ═════════════
  Vectors + Metadata  ──▶  Pinecone Upsert  ──▶  Searchable Index
                            │
                            ├── namespace: "resume"
                            └── namespace: "github"
```

---

## 5. Error Handling Flow

```
  User asks question
        │
        ▼
  Search Pinecone ──▶ No relevant chunks found?
        │                     │
        │ YES                 │ YES
        ▼                     ▼
  Build RAG prompt       "I don't have specific
        │                 information about that.
        ▼                 Let me share what I do know..."
  NVIDIA NIM responds
        │
        ▼
  Response references
  retrieved context? ──▶ NO ──▶ Flag as potential hallucination
        │
        │ YES
        ▼
  Return grounded answer ✅
```

---

## 6. Prompt Injection Defense Flow

```
  User input received
        │
        ▼
  ┌─────────────────┐
  │ Input Sanitizer  │
  │                   │
  │ • Strip "ignore   │
  │   instructions"  │
  │ • Detect role     │
  │   override        │
  │ • Flag suspicious │
  │   patterns        │
  └────────┬──────────┘
           │
     Suspicious?
      │        │
     YES       NO
      │        │
      ▼        ▼
  "I'm designed    Normal RAG
   to stay focused  pipeline
   on Anurag's
   background..."
```
