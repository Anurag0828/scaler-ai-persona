import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/chat"

test_cases = [
    {
        "id": "q1",
        "query": "Tell me about Anurag's experience with Autonomous AI Agents.",
        "expected_concept": "financial-adjustments-agent, multi-agent"
    },
    {
        "id": "q2",
        "query": "What are some specific performance improvements Anurag achieved in previous roles?",
        "expected_concept": "40%, memory usage, 90%"
    },
    {
        "id": "q3",
        "query": "Where did Anurag study and what was his degree?",
        "expected_concept": "B.Tech, Computer Science, Graphic Era"
    },
    {
        "id": "q4",
        "query": "Does Anurag have experience with any vector databases?",
        "expected_concept": "Pinecone, ChromaDB"
    },
    {
        "id": "q5_hallucination",
        "query": "What work did Anurag do at Google?",
        "expected_concept": "I don't have specific information"
    }
]

def run_chat_eval():
    results = []
    
    print("Running Chat Evals...")
    for idx, case in enumerate(test_cases):
        print(f"[{idx+1}/{len(test_cases)}] Testing: {case['query']}")
        start_time = time.time()
        
        try:
            r = requests.post(
                API_URL, 
                json={"message": case["query"]}, 
                stream=True
            )
            
            response_text = ""
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data: '):
                        data_str = decoded[6:]
                        try:
                            data = json.loads(data_str)
                            if 'token' in data:
                                response_text += data['token']
                        except:
                            pass
                            
            latency = time.time() - start_time
            
            # Simple keyword matching for evaluation (in reality, we'd use LLM-as-a-judge)
            keywords = [k.strip().lower() for k in case["expected_concept"].split(',')]
            matched = any(kw in response_text.lower() for kw in keywords)
            
            if "hallucination" in case["id"]:
                # If it's a hallucination test, pass if it admits it doesn't know
                passed = "don't" in response_text.lower() or "not" in response_text.lower()
            else:
                passed = matched
                
            results.append({
                "id": case["id"],
                "query": case["query"],
                "response": response_text[:100] + "...",
                "latency_sec": round(latency, 2),
                "passed": passed
            })
            
        except Exception as e:
            print(f"Error testing case {case['id']}: {e}")
            results.append({
                "id": case["id"],
                "query": case["query"],
                "error": str(e),
                "passed": False
            })
            
    # Save results
    with open("eval/chat_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nSaved results to eval/chat_results.json")
    
    passes = sum(1 for r in results if r["passed"])
    print(f"Passed: {passes}/{len(results)} ({passes/len(results)*100}%)")

if __name__ == "__main__":
    run_chat_eval()
