# 📐 Software Requirements Specification (SRS)

**Project**: Scaler AI Persona  
**Version**: 1.0  
**Date**: 2026-05-28  

---

## 1. Functional Requirements

### FR-1: Data Ingestion

| ID | Requirement | Priority |
|----|------------|----------|
| FR-1.1 | System shall parse resume from PDF or plain text | Must |
| FR-1.2 | System shall fetch all public GitHub repos via API | Must |
| FR-1.3 | System shall extract README, languages, and recent commits per repo | Must |
| FR-1.4 | System shall chunk text (500 chars, 100 overlap) | Must |
| FR-1.5 | System shall embed chunks using NVIDIA NIM embedding model | Must |
| FR-1.6 | System shall store vectors in Pinecone with metadata | Must |

### FR-2: RAG Engine

| ID | Requirement | Priority |
|----|------------|----------|
| FR-2.1 | Given a user query, retrieve top-5 relevant chunks from Pinecone | Must |
| FR-2.2 | Build prompt: system prompt + retrieved context + user message | Must |
| FR-2.3 | Generate response using NVIDIA NIM LLM | Must |
| FR-2.4 | Stream response tokens to client | Must |
| FR-2.5 | If no relevant context found, respond honestly ("I don't have that info") | Must |

### FR-3: Voice Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-3.1 | Provide a callable US phone number | Must |
| FR-3.2 | AI introduces itself as Anurag's AI representative | Must |
| FR-3.3 | Handle natural conversation (no rigid Q&A trees) | Must |
| FR-3.4 | Handle barge-in/interruptions without crashing | Must |
| FR-3.5 | Trigger `check_availability` tool when user asks to book | Must |
| FR-3.6 | Trigger `book_meeting` tool to confirm a booking | Must |
| FR-3.7 | Gracefully recover when it doesn't know something | Must |

### FR-4: Chat Interface

| ID | Requirement | Priority |
|----|------------|----------|
| FR-4.1 | Serve a public URL accessible without login | Must |
| FR-4.2 | Accept text input and display AI responses | Must |
| FR-4.3 | Stream responses with typing effect | Should |
| FR-4.4 | Answer questions about resume accurately | Must |
| FR-4.5 | Answer questions about GitHub repos accurately | Must |
| FR-4.6 | Allow availability check and booking from chat | Must |
| FR-4.7 | Resist prompt injection and adversarial probing | Must |

### FR-5: Calendar Integration

| ID | Requirement | Priority |
|----|------------|----------|
| FR-5.1 | Fetch available slots from Cal.com API | Must |
| FR-5.2 | Create confirmed booking via Cal.com API | Must |
| FR-5.3 | Return booking confirmation details to user | Must |

---

## 2. Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|------------|--------|
| NFR-1 | Latency | Voice first-response < 2s | Must |
| NFR-2 | Latency | Chat first-token < 3s | Must |
| NFR-3 | Availability | System live for 7+ days post-submission | Must |
| NFR-4 | Accuracy | Hallucination rate < 5% | Must |
| NFR-5 | Accuracy | RAG retrieval precision > 85% | Should |
| NFR-6 | Reliability | Booking success rate > 80% | Must |
| NFR-7 | Security | No API keys exposed in client code | Must |
| NFR-8 | Security | Prompt injection resistance | Must |
| NFR-9 | Cost | Total cost ≤ ₹0 (free tiers only) | Must |

---

## 3. System Interfaces

### External APIs

| API | Base URL | Auth | Purpose |
|-----|----------|------|---------|
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | Bearer token | LLM + Embeddings |
| Pinecone | `https://<index>.svc.pinecone.io` | API key header | Vector search |
| Cal.com | `https://api.cal.com/v2` | Bearer token | Calendar slots + booking |
| GitHub | `https://api.github.com` | Optional token | Repo data fetching |
| Vapi | `https://api.vapi.ai` | Bearer token | Voice agent config |

---

## 4. Data Dictionary

### Pinecone Vector Record

```json
{
  "id": "resume_chunk_001",
  "values": [0.012, -0.045, ...],  // 1024-dim embedding
  "metadata": {
    "source": "resume",            // "resume" | "github" | "talking_points"
    "section": "experience",       // section of document
    "repo_name": null,             // only for github source
    "text": "Anurag has 2 years..."  // original chunk text
  }
}
```

### Chat Request/Response

```json
// POST /chat - Request
{
  "message": "What projects has Anurag built?",
  "conversation_history": [...]
}

// Response (SSE Stream)
data: {"token": "Anurag"}
data: {"token": " has"}
data: {"token": " built"}
data: {"token": "..."}
data: {"done": true}
```

### Vapi Webhook Payload

```json
// POST /vapi-webhook
{
  "message": {
    "type": "function-call",
    "functionCall": {
      "id": "call_abc123",
      "name": "check_availability",
      "parameters": {
        "date": "2026-06-02"
      }
    }
  }
}

// Response
{
  "results": [{
    "toolCallId": "call_abc123",
    "result": "Available slots on June 2: 10:00 AM, 2:00 PM, 4:00 PM IST"
  }]
}
```
