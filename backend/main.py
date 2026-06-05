import logging
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scaler AI Persona Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://scaler-ai-persona-pi.vercel.app",
        "https://*.vercel.app",
        "*"  # Keep wildcard as fallback during development
    ],
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
        expected = config.VAPI_WEBHOOK_SECRET.strip()
        provided = secret.strip() if secret else ""
        if provided != expected:
            logger.warning(f"[AUTH] Vapi secret mismatch. Expected: '{expected[:4]}...', Got: '{provided[:4]}...'")
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "pinecone": "configured" if config.PINECONE_API_KEY else "missing",
            "nvidia_nim": "configured" if config.NVIDIA_API_KEY else "missing",
            "cal_com": "configured" if config.CAL_API_KEY else "missing",
            "cal_event_type": "configured" if config.CAL_EVENT_TYPE_ID else "missing"
        }
    }

@app.get("/keep-alive")
async def keep_alive():
    """Endpoint to prevent Render cold starts. Hit this every 10 min."""
    return {"status": "warm", "message": "Backend is alive"}

CALENDAR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available calendar slots for a specific date in YYYY-MM-DD format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format."
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_meeting",
            "description": "Book a meeting on the calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the attendee."
                    },
                    "email": {
                        "type": "string",
                        "description": "The email of the attendee."
                    },
                    "start_time": {
                        "type": "string",
                        "description": "The exact start time string of the slot as returned by check_availability (e.g. '2026-06-08T15:00:00.000+05:30'). Do NOT modify the timezone offset or convert to UTC/Z."
                    }
                },
                "required": ["name", "email", "start_time"]
            }
        }
    }
]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """RAG-powered chat endpoint with streaming SSE and tool-calling capabilities for Cal.com booking"""
    try:
        logger.info(f"[CHAT] Received message: {request.message[:100]}")
        
        # Check if the query is related to scheduling or booking
        booking_keywords = ["book", "schedule", "appoint", "calendar", "slot", "interview", "call", "meet", "availab"]
        is_booking_context = False
        
        if any(kw in request.message.lower() for kw in booking_keywords):
            is_booking_context = True
            
        if not is_booking_context and request.conversation_history:
            last_assistant_msg = None
            for msg in reversed(request.conversation_history):
                if msg.role == "assistant":
                    last_assistant_msg = msg.content.lower()
                    break
            if last_assistant_msg:
                context_keywords = ["date", "time", "slot", "email", "name", "calendar", "availab", "book"]
                if any(kw in last_assistant_msg for kw in context_keywords):
                    is_booking_context = True
                    
        # RAG Override: if user explicitly asks a general background/projects question during booking
        rag_override_keywords = ["what", "how", "why", "who", "tell", "show", "experience", "skill", "project", "resume", "work", "job", "background", "education", "cynoteck", "financial"]
        if is_booking_context and any(kw in request.message.lower() for kw in rag_override_keywords):
            is_booking_context = False
            
        # Build messages array
        from datetime import datetime
        current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
        system_prompt = CHAT_SYSTEM_PROMPT.replace("{{currentDateTime}}", current_date_str)
        system_prompt += f"\nToday is {current_date_str}."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history (last 6 messages)
        history = request.conversation_history[-6:] if len(request.conversation_history) > 6 else request.conversation_history
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
            
        if is_booking_context:
            logger.info("[CHAT] Booking context detected. Skipping RAG search.")
            messages.append({"role": "user", "content": request.message})
        else:
            logger.info("[CHAT] General context detected. Running RAG search.")
            context = await search_knowledge(request.message)
            rag_prompt = get_rag_prompt(context, request.message)
            messages.append({"role": "user", "content": rag_prompt})
            
        from .rag_engine import client
        
        if not is_booking_context:
            logger.info("[CHAT] Streaming general query response directly...")
            response = await client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            async def event_generator_direct():
                try:
                    async for chunk in response:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta.content
                            if delta:
                                yield {"data": json.dumps({"token": delta})}
                    yield {"data": json.dumps({"done": True})}
                except Exception as e:
                    logger.error(f"Streaming error: {e}", exc_info=True)
                    yield {"data": json.dumps({"error": str(e)})}
                    
            return EventSourceResponse(event_generator_direct())
        
        # 4. Booking path: First call (non-streaming) to check if the model wants to call tools
        logger.info("[CHAT] Booking context detected. Sending first LLM call with tools...")
        response = await client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            tools=CALENDAR_TOOLS,
            tool_choice="auto"
        )
        
        message_obj = response.choices[0].message
        tool_calls = message_obj.tool_calls
        
        # If the model wants to call tools
        if tool_calls:
            logger.info(f"[CHAT] LLM requested {len(tool_calls)} tool call(s)")
            messages.append(message_obj)
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_id = tool_call.id
                
                logger.info(f"[CHAT] Running tool: {tool_name} with args: {tool_args}")
                
                tool_result = ""
                try:
                    if tool_name == "check_availability":
                        date = tool_args.get("date")
                        slots = await get_available_slots(date)
                        if slots:
                            has_proposed_time = False
                            time_keywords = ["am", "pm", ":", "o'clock", "noon", "morning", "afternoon", "evening"]
                            if any(kw in request.message.lower() for kw in time_keywords):
                                has_proposed_time = True
                            if not has_proposed_time and request.conversation_history:
                                for msg in request.conversation_history:
                                    if msg.role == "user" and any(kw in msg.content.lower() for kw in time_keywords):
                                        has_proposed_time = True
                                        break
                            if not has_proposed_time:
                                logger.info("[CHAT] No specific time proposed. Limiting to top 3 slots.")
                                slots = slots[:3]
                            tool_result = f"Available slots on {date}: {json.dumps(slots)}"
                        else:
                            tool_result = f"No available slots found on {date}."
                    elif tool_name == "book_meeting":
                        name = tool_args.get("name")
                        email = tool_args.get("email")
                        start_time = tool_args.get("start_time")
                        res = await book_meeting(name, email, start_time)
                        if res.get("success"):
                            tool_result = f"Successfully booked the meeting for {start_time}."
                        else:
                            tool_result = f"Failed to book the meeting: {res.get('error')}"
                    else:
                        tool_result = f"Unknown tool: {tool_name}"
                except Exception as e:
                    logger.error(f"[CHAT] Error running tool {tool_name}: {e}", exc_info=True)
                    tool_result = f"Error executing tool: {str(e)}"
                
                logger.info(f"[CHAT] Tool {tool_name} result: {tool_result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "name": tool_name,
                    "content": tool_result
                })
            
            # Now call again with streaming to get the final answer
            logger.info("[CHAT] Sending second LLM call (streaming)...")
            final_response = await client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            async def event_generator():
                try:
                    async for chunk in final_response:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta.content
                            if delta:
                                yield {"data": json.dumps({"token": delta})}
                    yield {"data": json.dumps({"done": True})}
                except Exception as e:
                    logger.error(f"Streaming error: {e}", exc_info=True)
                    yield {"data": json.dumps({"error": str(e)})}
                    
            return EventSourceResponse(event_generator())
            
        else:
            # If no tool calls, stream the text we already got
            logger.info("[CHAT] No tools requested. Streaming text response...")
            content = message_obj.content
            
            async def event_generator_simple():
                if content:
                    chunk_size = 8
                    for i in range(0, len(content), chunk_size):
                        yield {"data": json.dumps({"token": content[i:i+chunk_size]})}
                yield {"data": json.dumps({"done": True})}
                
            return EventSourceResponse(event_generator_simple())
            
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
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
        logger.info(f"[WEBHOOK] Received Vapi webhook call")
        result = await handle_vapi_webhook(payload)
        logger.info(f"[WEBHOOK] Returning result: {json.dumps(result)[:500]}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        # Vapi expects a 200 OK even if we have an internal error, with a formatted response
        return JSONResponse(content={
            "results": [
                {"result": f"An internal error occurred: {str(e)}"}
            ]
        })
