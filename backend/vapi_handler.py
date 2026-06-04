import json
from .rag_engine import search_knowledge
from .calendar_service import get_available_slots, book_meeting

async def handle_vapi_webhook(payload: dict) -> dict:
    """
    Handle incoming tool calls from Vapi voice agent.
    Returns the appropriately formatted result object.
    """
    message = payload.get("message", {})
    message_type = message.get("type")
    
    call_id = None
    name = None
    parameters = {}
    
    if message_type == "function-call":
        function_call = message.get("functionCall", {})
        call_id = function_call.get("id")
        name = function_call.get("name")
        parameters = function_call.get("parameters", {})
    elif message_type == "tool-calls":
        tool_calls = message.get("toolCallList", [])
        if tool_calls:
            tool_call = tool_calls[0]
            call_id = tool_call.get("id")
            func = tool_call.get("function", {})
            name = func.get("name")
            args = func.get("arguments", "{}")
            if isinstance(args, str):
                import json
                try:
                    parameters = json.loads(args)
                except:
                    parameters = {}
            else:
                parameters = args
                
    if not call_id or not name:
        return {}
    
    print(f"Vapi requested tool: {name} with args: {parameters}")
    
    result_text = "I'm having trouble performing that action right now."
    
    try:
        if name == "search_knowledge":
            query = parameters.get("query", "")
            if query:
                result_text = await search_knowledge(query)
                # Keep it concise for voice
                if len(result_text) > 1000:
                    result_text = result_text[:1000] + "... [context truncated]"
            else:
                result_text = "No query provided."
                
        elif name == "check_availability":
            date = parameters.get("date", "")
            if date:
                slots = await get_available_slots(date)
                if slots:
                    result_text = f"Available slots on {date}: {json.dumps(slots)}"
                else:
                    result_text = f"No available slots found on {date}."
            else:
                result_text = "No date provided."
                
        elif name == "book_meeting":
            attendee_name = parameters.get("name", "Caller")
            email = parameters.get("email", "")
            start_time = parameters.get("start_time", "")
            
            if attendee_name and email and start_time:
                response = await book_meeting(attendee_name, email, start_time)
                if response.get("success"):
                    result_text = f"Successfully booked the meeting for {start_time}."
                else:
                    result_text = f"Failed to book the meeting: {response.get('error')}"
            else:
                result_text = "Missing required booking details (name, email, or start_time)."
        else:
            result_text = f"Unknown tool: {name}"
            
    except Exception as e:
        print(f"Error executing tool {name}: {e}")
        result_text = f"An error occurred while executing {name}."
        
    return {
        "results": [
            {
                "toolCallId": call_id,
                "result": result_text
            }
        ]
    }
