# 🔌 API Specification

**Project**: Scaler AI Persona  
**Version**: 1.0  
**Base URL**: `https://<app-name>.onrender.com`  

---

## 1. Chat Endpoint

### `POST /chat`

Send a user message and receive a streamed AI response grounded in RAG context.

**Request:**
```json
{
  "message": "What projects has Anurag built?",
  "conversation_history": [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! I'm Anurag's AI assistant."}
  ]
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"token": "Anurag"}
data: {"token": " has"}
data: {"token": " built"}
data: {"token": " several"}
data: {"token": " projects..."}
data: {"done": true, "sources": ["resume_chunk_3", "github_rag_project"]}
```

**Error Response:**
```json
{"error": "Rate limit exceeded", "status": 429}
```

---

## 2. Availability Endpoint

### `GET /availability?date=2026-06-02&timezone=Asia/Kolkata`

Fetch available calendar slots for a given date.

**Query Params:**
| Param | Type | Required | Default |
|-------|------|----------|---------|
| `date` | string (YYYY-MM-DD) | Yes | — |
| `timezone` | string | No | `Asia/Kolkata` |

**Response:**
```json
{
  "date": "2026-06-02",
  "timezone": "Asia/Kolkata",
  "slots": [
    {"start": "2026-06-02T10:00:00+05:30", "end": "2026-06-02T10:30:00+05:30"},
    {"start": "2026-06-02T14:00:00+05:30", "end": "2026-06-02T14:30:00+05:30"},
    {"start": "2026-06-02T16:00:00+05:30", "end": "2026-06-02T16:30:00+05:30"}
  ]
}
```

---

## 3. Booking Endpoint

### `POST /book`

Book a confirmed meeting on the calendar.

**Request:**
```json
{
  "name": "Scaler Evaluator",
  "email": "evaluator@scaler.com",
  "start_time": "2026-06-02T14:00:00+05:30",
  "notes": "Interview discussion"
}
```

**Response:**
```json
{
  "success": true,
  "booking": {
    "id": "booking_abc123",
    "title": "Interview with Anurag Sajwan",
    "start": "2026-06-02T14:00:00+05:30",
    "end": "2026-06-02T14:30:00+05:30",
    "attendees": ["evaluator@scaler.com", "anurag@email.com"],
    "meeting_link": "https://cal.com/anurag/meeting-abc123"
  }
}
```

---

## 4. Vapi Webhook

### `POST /vapi-webhook`

Receives tool call requests from Vapi voice agent.

**Request (function-call):**
```json
{
  "message": {
    "type": "function-call",
    "functionCall": {
      "id": "call_xyz789",
      "name": "check_availability",
      "parameters": {"date": "2026-06-02"}
    }
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "toolCallId": "call_xyz789",
      "result": "Available slots on June 2, 2026: 10:00 AM, 2:00 PM, 4:00 PM IST"
    }
  ]
}
```

**Supported Tool Functions:**

| Function Name | Parameters | Description |
|--------------|-----------|-------------|
| `search_knowledge` | `{"query": "string"}` | RAG search over resume/GitHub data |
| `check_availability` | `{"date": "YYYY-MM-DD"}` | Fetch open calendar slots |
| `book_meeting` | `{"name", "email", "start_time"}` | Book confirmed meeting |

---

## 5. Health Check

### `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "pinecone": "connected",
    "nvidia_nim": "connected",
    "cal_com": "connected"
  },
  "uptime_seconds": 86400
}
```

---

## 6. Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/chat` | 10 requests | per minute per IP |
| `/availability` | 20 requests | per minute |
| `/book` | 5 requests | per minute |
| `/vapi-webhook` | 30 requests | per minute |

---

## 7. Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Normal response |
| 400 | Bad Request | Missing required field |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | NVIDIA NIM / Pinecone down |
| 503 | Service Unavailable | Cold start (Render) |
