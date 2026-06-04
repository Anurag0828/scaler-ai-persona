# AI Persona Evaluation Report

## Executive Summary
This report evaluates the performance of Anurag Sajwan's AI Persona (Scaler Screening Assignment).

### Core Metrics
- **Retrieval Accuracy**: 60.0% (3/5 test cases passed)
- **Average Chat Latency (TTFT)**: 15.90 seconds
- **Hallucination Rate**: 0% (Agent correctly refuses to answer out-of-domain questions)

## Methodology
- **RAG Engine**: Pinecone Vector DB + NVIDIA NIM (`nv-embedqa-e5-v5` & `llama-3.1-70b-instruct`).
- **Test Strategy**: Golden Q&A set covering past experience, specific GitHub repositories, and hallucination prompts.

## Test Cases Breakdown

### Test: Tell me about Anurag's experience with Autonomous AI Agents.
- **Status**: ✅ PASS
- **Latency**: 19.24s
- **Response Snippet**: **Autonomous AI Agents Experience**
=====================================

Anurag has experience wit...

### Test: What are some specific performance improvements Anurag achieved in previous roles?
- **Status**: ❌ FAIL
- **Latency**: 8.75s
- **Response Snippet**: **Specific Performance Improvements Achieved by Anurag**

Based on his resume, Anurag achieved the f...

### Test: Where did Anurag study and what was his degree?
- **Status**: ✅ PASS
- **Latency**: 20.91s
- **Response Snippet**: **Education Background**
Anurag Sajwan studied at DIT University, Dehradun, India, where he pursued ...

### Test: Does Anurag have experience with any vector databases?
- **Status**: ❌ FAIL
- **Latency**: 5.91s
- **Response Snippet**: **Vector Database Experience**
Anurag has experience with vector databases, specifically with pgvect...

### Test: What work did Anurag do at Google?
- **Status**: ✅ PASS
- **Latency**: 24.67s
- **Response Snippet**: **No Specific Information Found**

I don't have specific information about Anurag working at Google ...
