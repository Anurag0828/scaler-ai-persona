# 💰 Cost Analysis

**Project**: Scaler AI Persona  
**Date**: 2026-05-28  

---

## 1. Total Cost Summary

| | Monthly Cost | Setup Cost |
|---|---|---|
| **Grand Total** | **₹0** | **₹0** |

> All services use free tiers. No credit card required for any.

---

## 2. Per-Service Breakdown

| Service | Free Tier | Our Usage | Fits Free Tier? |
|---------|-----------|-----------|-----------------|
| **NVIDIA NIM** | 1,000 credits (no expiry) | ~200 credits (eval + live usage) | ✅ Yes |
| **Vapi** | $10 trial credits | ~$3-5 for testing + live calls | ✅ Yes |
| **Pinecone** | 2GB, 100K vectors | ~500 vectors (~2MB) | ✅ Yes |
| **Cal.com** | Unlimited bookings | ~20 bookings | ✅ Yes |
| **Vercel** | 100GB bandwidth | ~1GB | ✅ Yes |
| **Render** | 750 hours/month | 1 service = ~720 hours | ✅ Yes |
| **GitHub** | Unlimited public repos | 1 repo | ✅ Yes |
| **Deepgram** | $200 credit (via Vapi) | Included in Vapi credits | ✅ Yes |

---

## 3. Per-Interaction Cost Estimates

### Voice Call (via Vapi)
```
Avg call duration: 3 minutes

Vapi platform:     ~$0.05/min  = $0.15
Deepgram STT:      ~$0.01/min  = $0.03
TTS:               ~$0.02/min  = $0.06
NVIDIA NIM:        ~2-3 credits = $0.00 (free)
────────────────────────────────────────
Total per call:                  ~$0.24
$10 trial ÷ $0.24 =             ~41 calls available
```

### Chat Session (via Backend)
```
Avg session: 5 messages

Pinecone queries:   5 × free    = $0.00
NVIDIA NIM:         5 credits   = $0.00
Vercel bandwidth:   ~50KB       = $0.00
Render compute:     free tier   = $0.00
────────────────────────────────────────
Total per session:               $0.00
```

---

## 4. Usage Budget for 7-Day Live Period

| Activity | Volume | Cost |
|----------|--------|------|
| Scaler evaluation calls | ~5-10 calls | ~$2.40 |
| Your test calls | ~10 calls | ~$2.40 |
| Chat sessions | ~50 sessions | $0.00 |
| Keep-alive pings (Render) | 1008 pings | $0.00 |
| **Total 7-day cost** | | **~$4.80** |

> Fits within Vapi's $10 free trial. No other paid costs.

---

## 5. Scaling Costs (If Needed)

| Scale | Monthly Cost |
|-------|-------------|
| 50 calls + 100 chats/mo | ~$0 (free tiers) |
| 500 calls + 1000 chats/mo | ~$120/mo |
| 5000 calls + 10000 chats/mo | ~$800/mo |

### Cost Breakdown at Scale (500 calls/mo):
```
Vapi:        500 × $0.24 = $120/mo
NVIDIA NIM:  request more credits or switch to self-hosted
Pinecone:    still free at this scale
Render:      upgrade to Starter = $7/mo
Vercel:      still free at this scale
Cal.com:     still free
─────────────────────────────────────
Total:       ~$127/mo
```

---

## 6. Cost Optimization Strategies

1. **Cache frequent RAG queries** — Avoid repeated Pinecone + NIM calls for common questions
2. **Keep Render warm** — Prevent cold starts (saves latency, not money)
3. **Use smaller LLM for simple queries** — Route greetings to cheaper/faster model
4. **Monitor Vapi dashboard** — Track credit usage daily during live period
5. **Set usage alerts** — Get notified at 50% and 80% credit usage
