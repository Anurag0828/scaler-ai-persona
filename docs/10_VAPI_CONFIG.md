# 📞 Vapi Voice Agent Configuration

**Project**: Scaler AI Persona  
**Version**: 1.0  
**Date**: 2026-06-04  
**Purpose**: Complete Vapi assistant configuration blueprint — every setting needed to create the voice agent.

---

## 1. Assistant Configuration (JSON)

> This is the exact JSON payload to create the Vapi assistant via `POST https://api.vapi.ai/assistant`

```json
{
  "name": "Anurag Sajwan AI Persona",
  
  "model": {
    "provider": "custom-llm-url",
    "url": "https://<backend-app>.onrender.com/vapi-llm",
    "model": "meta/llama-3.1-70b-instruct",
    "temperature": 0.7,
    "maxTokens": 300,
    "messages": [
      {
        "role": "system",
        "content": "<<< PASTE VOICE SYSTEM PROMPT FROM 08_SYSTEM_PROMPTS.md >>>"
      }
    ]
  },

  "voice": {
    "provider": "11labs",
    "voiceId": "pNInz6obpgDQGcFmaJgB",
    "stability": 0.6,
    "similarityBoost": 0.75,
    "speed": 1.0
  },

  "transcriber": {
    "provider": "deepgram",
    "model": "nova-2",
    "language": "en",
    "smartFormat": true,
    "keywords": ["Anurag:3", "Sajwan:3", "Scaler:2"]
  },

  "firstMessage": "Hi! I'm Anurag's AI representative. I'm here to tell you about his background, skills, and projects — and I can also help you schedule an interview with him. What would you like to know?",
  
  "firstMessageMode": "assistant-speaks-first",

  "hipaaEnabled": false,
  "recordingEnabled": true,
  "endCallFunctionEnabled": true,
  
  "serverUrl": "https://<backend-app>.onrender.com/vapi-webhook",
  "serverUrlSecret": "<VAPI_WEBHOOK_SECRET>",

  "silenceTimeoutSeconds": 30,
  "maxDurationSeconds": 600,
  "backgroundSound": "office",
  "backchannelingEnabled": true,
  "backgroundDenoisingEnabled": true,

  "endCallMessage": "Thanks for your interest in Anurag! If you booked a meeting, you'll receive a calendar invite shortly. Have a great day!",

  "clientMessages": [
    "transcript",
    "hang",
    "function-call",
    "speech-update",
    "status-update",
    "conversation-update"
  ],

  "serverMessages": [
    "end-of-call-report",
    "status-update",
    "hang",
    "function-call",
    "transcript"
  ]
}
```

---

## 2. Tool Function Definitions

These are the functions the Vapi assistant can call during a conversation. They are handled by the FastAPI backend at `/vapi-webhook`.

### Tool 1: `search_knowledge`

```json
{
  "type": "function",
  "function": {
    "name": "search_knowledge",
    "description": "Search Anurag's knowledge base (resume, GitHub repos, talking points) to find relevant information for answering questions about his background, skills, projects, and experience. Use this tool BEFORE answering any factual question about Anurag.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query to look up in Anurag's knowledge base. Be specific — e.g., 'Python experience' or 'education background' or 'GitHub project tech stack'"
        }
      },
      "required": ["query"]
    }
  }
}
```

### Tool 2: `check_availability`

```json
{
  "type": "function",
  "function": {
    "name": "check_availability",
    "description": "Check Anurag's real calendar availability for a specific date. Returns available time slots that can be booked for an interview. Use this when the caller wants to schedule a meeting.",
    "parameters": {
      "type": "object",
      "properties": {
        "date": {
          "type": "string",
          "description": "The date to check availability for, in YYYY-MM-DD format. Example: '2026-06-05'"
        }
      },
      "required": ["date"]
    }
  }
}
```

### Tool 3: `book_meeting`

```json
{
  "type": "function",
  "function": {
    "name": "book_meeting",
    "description": "Book a confirmed interview meeting on Anurag's calendar. Use this AFTER the caller has chosen a specific time slot and provided their name and email.",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Full name of the person booking the meeting"
        },
        "email": {
          "type": "string",
          "description": "Email address of the person booking the meeting"
        },
        "start_time": {
          "type": "string",
          "description": "The chosen meeting start time in ISO 8601 format. Example: '2026-06-05T14:00:00+05:30'"
        }
      },
      "required": ["name", "email", "start_time"]
    }
  }
}
```

---

## 3. Voice Selection Guide

### Recommended Voices (ElevenLabs via Vapi)

| Voice ID | Name | Style | Best For |
|----------|------|-------|----------|
| `pNInz6obpgDQGcFmaJgB` | Adam | Professional, clear, male | ✅ **Primary choice** — professional AI representative |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Professional, female | Alternative if preferred |
| `ErXwobaYiN019PkySvjV` | Antoni | Warm, conversational, male | More casual option |

### Voice Settings Explained

| Setting | Value | Why |
|---------|-------|-----|
| `stability` | `0.6` | Slightly lower = more natural variation (less robotic) |
| `similarityBoost` | `0.75` | Higher = more consistent voice quality |
| `speed` | `1.0` | Normal pace — can increase to 1.1 if responses feel slow |

> **NOTE**: Vapi also supports its own built-in voices (no ElevenLabs needed). If ElevenLabs credits are a concern, use Vapi's default `PlayHT` or `Azure` voices — they're included in the $10 trial.

---

## 4. Transcriber Settings (Deepgram)

| Setting | Value | Purpose |
|---------|-------|---------|
| `model` | `nova-2` | Best accuracy + lowest latency on Deepgram |
| `language` | `en` | English language recognition |
| `smartFormat` | `true` | Auto-formats numbers, dates, punctuation |
| `keywords` | `["Anurag:3", "Sajwan:3", "Scaler:2"]` | Boosts recognition of key proper nouns (0-5 scale) |

---

## 5. Latency Optimization Settings

### Target: < 2 Second First Response

```
Total latency budget: 2000ms

Breakdown:
├── STT (Deepgram Nova-2):         ~200ms
├── Network to backend:             ~100ms  
├── RAG retrieval (Pinecone):       ~200ms
├── LLM generation (NVIDIA NIM):    ~800ms (first token)
├── TTS (ElevenLabs):               ~300ms
└── Network overhead:               ~200ms
                                   ────────
Total estimated:                   ~1800ms ✅
```

### Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Skip RAG for greetings** | If message is "hi/hello/hey", respond directly without search | -400ms for greeting |
| **Streaming LLM** | Stream tokens to TTS as they arrive | -500ms perceived |
| **Cache frequent queries** | Redis/in-memory cache for top 20 questions | -1000ms for cached |
| **Warm Render** | Keep-alive ping every 10 min | Prevents 5-30s cold start |
| **Short first message** | Keep `firstMessage` under 25 words | Faster TTS rendering |

---

## 6. Interruption & Barge-In Handling

### How Vapi Handles Barge-In (Default Behavior)
1. Caller starts speaking → Vapi detects speech via VAD (Voice Activity Detection)
2. Vapi immediately stops the assistant's TTS playback
3. New caller speech is transcribed
4. New transcription is sent to LLM as the next user turn
5. Assistant generates new response based on interrupted context

### Settings for Robust Barge-In

| Setting | Value | Why |
|---------|-------|-----|
| `backchannelingEnabled` | `true` | AI can say "mm-hmm", "right" during caller's speech |
| `backgroundDenoisingEnabled` | `true` | Prevents background noise from triggering false barge-in |
| `silenceTimeoutSeconds` | `30` | Waits 30s of silence before assuming caller hung up |
| `maxDurationSeconds` | `600` | 10-minute max call to prevent credit drain |

### Edge Cases to Handle
1. **Caller mumbles mid-sentence**: AI should wait for complete thought before responding
2. **Background noise triggers speech**: Denoising + higher VAD threshold
3. **Caller interrupts during tool call**: AI should say "One moment, I'm checking that for you"
4. **Long silence after question**: AI should gently prompt: "Are you still there? Feel free to ask anything!"

---

## 7. Webhook Payload Processing

### Incoming Webhook Structure (from Vapi)

```json
{
  "message": {
    "type": "function-call",
    "call": {
      "id": "call_abc123",
      "orgId": "org_xyz",
      "type": "inboundPhoneCall",
      "phoneNumberId": "pn_12345"
    },
    "functionCall": {
      "id": "tc_789",
      "name": "search_knowledge",
      "parameters": {
        "query": "What is Anurag's work experience?"
      }
    }
  }
}
```

### Backend Response Format (to Vapi)

```json
{
  "results": [
    {
      "toolCallId": "tc_789",
      "result": "Based on his resume, Anurag has worked at [Company] as a [Role] from [Date]. His key responsibilities included [details]. He also built [project] which [impact]."
    }
  ]
}
```

### Error Response Format

```json
{
  "results": [
    {
      "toolCallId": "tc_789",
      "result": "I'm having trouble retrieving that information right now. I'd recommend scheduling a direct call with Anurag to discuss this in detail."
    }
  ]
}
```

> **IMPORTANT**: Vapi expects the response within **20 seconds** or the tool call times out. Set backend timeout accordingly.

---

## 8. Phone Number Setup

### Steps to Get Free Phone Number
1. Sign up at [Vapi Dashboard](https://dashboard.vapi.ai)
2. Get $10 trial credits automatically (no credit card)
3. Go to **Phone Numbers** → **Buy Number**
4. Select **US number** (free with trial credits)
5. Assign assistant to the phone number
6. Note the `phoneNumberId` for `.env` config

### Estimated Call Budget
```
$10 trial credits
÷ $0.24 per 3-min call
= ~41 calls available

Budget allocation:
├── 15 test calls (development)
├── 10 evaluator calls (Scaler team)
└── 16 buffer calls
```

---

## 9. End-of-Call Report

Vapi sends an `end-of-call-report` webhook after each call. Use this for eval metrics.

```json
{
  "message": {
    "type": "end-of-call-report",
    "endedReason": "customer-ended-call",
    "call": {
      "id": "call_abc123",
      "duration": 185,
      "startedAt": "2026-06-04T10:00:00Z",
      "endedAt": "2026-06-04T10:03:05Z"
    },
    "recordingUrl": "https://...",
    "transcript": "...",
    "summary": "...",
    "cost": 0.24,
    "messages": [...]
  }
}
```

### Metrics to Extract for Eval Report
| Metric | How to Calculate |
|--------|-----------------|
| **First-response latency** | `messages[1].timestamp - messages[0].timestamp` |
| **Total call duration** | `call.duration` seconds |
| **Booking success** | Check if `book_meeting` tool was called AND returned success |
| **Turns per call** | `len(messages) / 2` |
| **Tool call count** | Count of `function-call` type messages |

---

## 10. Testing Checklist

### Pre-Launch Tests
- [ ] Call the number → AI picks up and greets
- [ ] Ask "Who are you?" → Identifies as Anurag's AI representative
- [ ] Ask about experience → Uses `search_knowledge` tool, returns grounded answer
- [ ] Ask about a GitHub repo → Returns accurate repo info
- [ ] Request interview booking → Full flow: check availability → select slot → provide details → confirm
- [ ] Interrupt mid-sentence → AI stops, responds to new input
- [ ] Ask something it doesn't know → Admits honestly, offers to book call
- [ ] Try prompt injection verbally → Stays in character
- [ ] Stay silent for 25s → AI prompts "Are you still there?"
- [ ] Ask in Hindi/another language → Responds in English, stays professional
- [ ] Make 3 consecutive calls → All work consistently, no state leakage

### Latency Tests
- [ ] Measure first-response latency across 5 calls → Average < 2s
- [ ] Test during peak hours (US business hours) → Still < 2s
- [ ] Test after Render cold start → Verify keep-alive prevents delay
