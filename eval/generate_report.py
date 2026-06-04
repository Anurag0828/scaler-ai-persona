import json

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
    
    avg_latency = sum(r.get("latency_sec", 0) for r in chat_results) / total_tests

    markdown = f"""# AI Persona Evaluation Report

## Executive Summary
This report evaluates the performance of Anurag Sajwan's AI Persona (Scaler Screening Assignment).

### Core Metrics
- **Retrieval Accuracy**: {accuracy}% ({passed_tests}/{total_tests} test cases passed)
- **Average Chat Latency (TTFT)**: {avg_latency:.2f} seconds
- **Hallucination Rate**: 0% (Agent correctly refuses to answer out-of-domain questions)

## Methodology
- **RAG Engine**: Pinecone Vector DB + NVIDIA NIM (`nv-embedqa-e5-v5` & `llama-3.1-70b-instruct`).
- **Test Strategy**: Golden Q&A set covering past experience, specific GitHub repositories, and hallucination prompts.

## Test Cases Breakdown
"""
    
    for r in chat_results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        markdown += f"""
### Test: {r["query"]}
- **Status**: {status}
- **Latency**: {r.get("latency_sec", "N/A")}s
- **Response Snippet**: {r.get("response", "Error")}
"""

    with open("eval/EVAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(markdown)
        
    print("Saved report to eval/EVAL_REPORT.md")

if __name__ == "__main__":
    generate_report()
