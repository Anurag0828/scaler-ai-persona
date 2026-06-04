from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import json
from pydantic import BaseModel
from typing import List, Optional

from .config import config
from .prompts import CHAT_SYSTEM_PROMPT, get_rag_prompt
from .rag_engine import search_knowledge, generate_chat_response
from .calendar_service import get_available_slots, book_meeting
from .vapi_handler import handle_vapi_webhook

app = FastAPI(title="Scaler AI Persona Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []

class BookingRequest(BaseModel):
    name: str
    email: str
    start_time: str

def verify_vapi_secret(request: Request):
    """Dependency to verify Vapi webhook secret"""
    if config.VAPI_WEBHOOK_SECRET:
        secret = request.headers.get("x-vapi-secret")
        if secret != config.VAPI_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "pinecone": "configured" if config.PINECONE_API_KEY else "missing",
            "nvidia_nim": "configured" if config.NVIDIA_API_KEY else "missing",
            "cal_com": "configured" if config.CAL_API_KEY else "missing"
        }
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """RAG-powered chat endpoint with streaming SSE"""
    try:
        # 1. Search knowledge base
        context = await search_knowledge(request.message)
        
        # 2. Build prompt
        rag_prompt = get_rag_prompt(context, request.message)
        
        # 3. Build messages array
        messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
        
        # Add history (last 6 messages)
        history = request.conversation_history[-6:] if len(request.conversation_history) > 6 else request.conversation_history
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
            
        # Add current augmented message
        messages.append({"role": "user", "content": rag_prompt})
        
        # 4. Generate streaming response
        response = await generate_chat_response(messages, stream=True)
        
        async def event_generator():
            try:
                async for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield {"data": json.dumps({"token": delta})}
                # Send done signal
                yield {"data": json.dumps({"done": True})}
            except Exception as e:
                print(f"Streaming error: {e}")
                yield {"data": json.dumps({"error": str(e)})}
                
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/availability")
async def availability_endpoint(date: str):
    """Proxy to Cal.com to fetch slots"""
    slots = await get_available_slots(date)
    return {"date": date, "slots": slots}

@app.post("/book")
async def book_endpoint(request: BookingRequest):
    """Proxy to Cal.com to book a meeting"""
    result = await book_meeting(request.name, request.email, request.start_time)
    if result.get("success"):
        return result
    raise HTTPException(status_code=400, detail=result.get("error"))

@app.post("/vapi-webhook")
async def vapi_webhook(request: Request, _ = Depends(verify_vapi_secret)):
    """Handle Vapi tool calls"""
    try:
        payload = await request.json()
        result = await handle_vapi_webhook(payload)
        return JSONResponse(content=result)
    except Exception as e:
        print(f"Webhook error: {e}")
        # Vapi expects a 200 OK even if we have an internal error, with a formatted response
        return JSONResponse(content={
            "results": [
                {"result": "An internal error occurred."}
            ]
        })
