import json
import os
from datetime import datetime

def generate_report():
    print("Generating Evaluation Report...")
    
    try:
        with open("eval/chat_results.json", "r") as f:
            chat_results = json.load(f)
    except FileNotFoundError:
        print("Run test_chat.py first!")
        return

    total_tests = len(chat_results)
    passed_tests = sum(1 for r in chat_results if r["passed"])
    accuracy = (passed_tests / total_tests) * 100
    
    latencies = [r.get("latency_sec", 0) for r in chat_results if "latency_sec" in r]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    
    # Per-category accuracy
    categories = {}
    for r in chat_results:
        cat = r.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "latencies": []}
        categories[cat]["total"] += 1
        if r["passed"]:
            categories[cat]["passed"] += 1
        if "latency_sec" in r:
            categories[cat]["latencies"].append(r["latency_sec"])
    
    # Hallucination rate
    hallucination_tests = [r for r in chat_results if r.get("type") == "hallucination"]
    hallucination_passes = sum(1 for r in hallucination_tests if r["passed"])
    hallucination_rate = ((len(hallucination_tests) - hallucination_passes) / len(hallucination_tests) * 100) if hallucination_tests else 0
    
    # Injection resistance
    injection_tests = [r for r in chat_results if r.get("type") == "injection"]
    injection_passes = sum(1 for r in injection_tests if r["passed"])
    
    # Failed tests
    failed_tests = [r for r in chat_results if not r["passed"]]
    
    now = datetime.now().strftime("%Y-%m-%d")

    markdown = f"""# AI Persona Evaluation Report

**Candidate**: Anurag Sajwan  
**Date**: {now}  
**System**: RAG-grounded Voice + Chat Agent (Scaler AI Engineer Screening)

---

## Executive Summary

This report evaluates the performance of Anurag Sajwan's autonomous AI persona across retrieval accuracy, latency, hallucination resistance, and prompt injection defense.

### Core Metrics

| Metric | Result | Target |
|--------|--------|--------|
| **Overall Retrieval Accuracy** | {accuracy:.0f}% ({passed_tests}/{total_tests}) | ≥ 80% |
| **Average Chat Latency (TTFT)** | {avg_latency:.1f}s | < 3s |
| **Latency Range** | {min_latency:.1f}s – {max_latency:.1f}s | — |
| **Hallucination Rate** | {hallucination_rate:.0f}% | < 5% |
| **Prompt Injection Resistance** | {injection_passes}/{len(injection_tests)} blocked | 100% |

---

## Per-Category Breakdown

| Category | Passed | Total | Accuracy | Avg Latency |
|----------|--------|-------|----------|-------------|
"""
    
    for cat, stats in categories.items():
        cat_accuracy = stats['passed'] / stats['total'] * 100
        cat_avg_latency = sum(stats['latencies']) / len(stats['latencies']) if stats['latencies'] else 0
        markdown += f"| {cat} | {stats['passed']} | {stats['total']} | {cat_accuracy:.0f}% | {cat_avg_latency:.1f}s |\n"

    markdown += """
---

## Architecture

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM (Chat) | NVIDIA NIM `llama-3.1-70b-instruct` | RAG-grounded chat responses |
| LLM (Voice) | GPT-4o-mini (via Vapi) | Conversational voice responses |
| Embeddings | NVIDIA NIM `nv-embedqa-e5-v5` | 1024-dim query/document embeddings |
| Vector DB | Pinecone (Serverless) | Cosine similarity search |
| Voice Agent | Vapi + Deepgram STT + ElevenLabs TTS | End-to-end voice pipeline |
| Calendar | Cal.com v2 API | Real-time availability + booking |
| Backend | FastAPI on Render | Webhook handler + RAG engine |
| Frontend | Next.js on Vercel | Streaming chat interface |

---

## Test Cases Detail
"""
    
    for r in chat_results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        latency = r.get("latency_sec", "N/A")
        latency_str = f"{latency}s" if isinstance(latency, (int, float)) else latency
        markdown += f"""
### [{r.get('category', '?')}] {r["query"]}
- **Status**: {status}
- **Type**: {r.get('type', 'factual')}
- **Latency**: {latency_str}
- **Response**: {r.get("response", r.get("error", "Error"))}
"""

    if failed_tests:
        markdown += """
---

## Failure Mode Analysis
"""
        for i, r in enumerate(failed_tests[:3], 1):
            markdown += f"""
### Failure {i}: {r["query"]}
- **Root Cause**: Retrieved context did not contain the expected information, or keyword match was too strict.
- **Category**: {r.get('category', 'Unknown')}
- **Potential Fix**: Improve chunking granularity for this category, add more targeted metadata, or expand keyword matching in eval.
"""

    markdown += f"""
---

## Conscious Tradeoff

**RAG vs. Fine-tuning**: Chose RAG (Retrieval-Augmented Generation) over fine-tuning because:
1. **Transparency**: Every answer can be traced to a specific source chunk — critical for an evaluation where grounding is measured.
2. **Cost**: Fine-tuning requires GPU hours and retraining on data changes. RAG requires only re-embedding.
3. **Freshness**: When resume or GitHub data changes, re-ingestion takes minutes, not hours.
4. **Tradeoff**: RAG has higher per-query latency (embedding + vector search + LLM) vs. a fine-tuned model that answers from parameters directly. Mitigated with Pinecone serverless (low-latency) and streaming responses.

---

## What I'd Build With 2 More Weeks

1. **LLM-as-a-Judge Evaluation**: Replace keyword matching with GPT-4 scoring each response on a 1-5 rubric for accuracy, relevance, and grounding. This would give more nuanced accuracy metrics.
2. **Hybrid Search (Vector + BM25)**: Add keyword-based BM25 search alongside vector search to catch exact-match queries that embedding similarity might miss (e.g., specific company names, tool names).
3. **Response Caching**: Cache the top 20 most-asked questions (from Vapi call logs) to reduce latency to near-zero for common queries.
4. **Streaming Voice with NIM**: Replace GPT-4o-mini in Vapi with a custom LLM endpoint streaming NVIDIA NIM responses, reducing dependency on OpenAI and keeping the entire stack open-source.
5. **End-of-Call Analytics Dashboard**: Parse Vapi's `end-of-call-report` webhooks to build a live dashboard showing call metrics, booking success rates, and common question patterns.
"""

    os.makedirs("eval", exist_ok=True)
    with open("eval/EVAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print(f"Saved report to eval/EVAL_REPORT.md")
    print(f"Overall accuracy: {accuracy:.0f}% ({passed_tests}/{total_tests})")

if __name__ == "__main__":
    generate_report()
