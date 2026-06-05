import json
import logging
from .rag_engine import search_knowledge
from .calendar_service import get_available_slots, book_meeting

logger = logging.getLogger(__name__)

async def handle_vapi_webhook(payload: dict) -> dict:
    """
    Handle incoming tool calls from Vapi voice agent.
    Supports multiple Vapi payload formats:
      - Legacy "function-call" format
      - New "tool-calls" format with toolCallList
      - New "tool-calls" format with toolCalls (alternate key)
    Returns the appropriately formatted result object.
    """
    # === CRITICAL: Log the raw payload for debugging ===
    logger.info(f"[VAPI] Raw payload received: {json.dumps(payload, indent=2)}")

    message = payload.get("message", {})
    message_type = message.get("type")

    logger.info(f"[VAPI] Message type: {message_type}")

    call_id = None
    name = None
    parameters = {}

    if message_type == "function-call":
        # Legacy format
        function_call = message.get("functionCall", {})
        call_id = function_call.get("id")
        name = function_call.get("name")
        parameters = function_call.get("parameters", {})
        logger.info(f"[VAPI] Parsed function-call: name={name}, id={call_id}")

    elif message_type == "tool-calls":
        # New format — try both known key names
        tool_calls = message.get("toolCallList") or message.get("toolCalls") or []

        if not tool_calls:
            # Fallback: check if tool calls are at the top level of the payload
            tool_calls = payload.get("toolCallList") or payload.get("toolCalls") or []

        logger.info(f"[VAPI] Found {len(tool_calls)} tool call(s)")

        if tool_calls:
            tool_call = tool_calls[0]
            call_id = tool_call.get("id")
            func = tool_call.get("function", {})
            name = func.get("name")
            args = func.get("arguments", "{}")

            if isinstance(args, str):
                try:
                    parameters = json.loads(args)
                except json.JSONDecodeError:
                    logger.warning(f"[VAPI] Failed to parse arguments string: {args}")
                    parameters = {}
            elif isinstance(args, dict):
                parameters = args
            else:
                parameters = {}

            logger.info(f"[VAPI] Parsed tool-call: name={name}, id={call_id}, params={parameters}")
        else:
            logger.warning(f"[VAPI] tool-calls type but no tool calls found in payload")
            logger.warning(f"[VAPI] Available message keys: {list(message.keys())}")
            logger.warning(f"[VAPI] Available top-level keys: {list(payload.keys())}")

    else:
        logger.warning(f"[VAPI] Unknown message type: {message_type}")
        logger.warning(f"[VAPI] Full message keys: {list(message.keys())}")
        # Return a helpful error instead of empty dict
        return {
            "results": [
                {"result": f"Unsupported message type: {message_type}"}
            ]
        }

    if not call_id or not name:
        logger.error(f"[VAPI] Missing call_id ({call_id}) or name ({name}). Cannot process.")
        logger.error(f"[VAPI] Full payload dump for debugging: {json.dumps(payload)}")
        return {
            "results": [
                {"result": "Unable to process the tool call. Missing call ID or function name."}
            ]
        }

    logger.info(f"[VAPI] Executing tool: {name} with args: {parameters}")

    result_text = "I'm having trouble performing that action right now."

    try:
        if name == "search_knowledge":
            query = parameters.get("query", "")
            if query:
                result_text = await search_knowledge(query)
                logger.info(f"[VAPI] search_knowledge returned {len(result_text)} chars")
                # Keep it concise for voice
                if len(result_text) > 5000:
                    result_text = result_text[:5000] + "... [context truncated]"
            else:
                result_text = "No query provided."
                logger.warning("[VAPI] search_knowledge called with empty query")

        elif name == "check_availability":
            date = parameters.get("date", "")
            if date:
                slots = await get_available_slots(date)
                if slots:
                    result_text = f"Available slots on {date}: {json.dumps(slots)}"
                else:
                    result_text = f"No available slots found on {date}."
                logger.info(f"[VAPI] check_availability for {date}: {result_text[:100]}")
            else:
                result_text = "No date provided."
                logger.warning("[VAPI] check_availability called with empty date")

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
                logger.info(f"[VAPI] book_meeting result: {result_text}")
            else:
                result_text = "Missing required booking details (name, email, or start_time)."
                logger.warning(f"[VAPI] book_meeting missing fields: name={attendee_name}, email={email}, start_time={start_time}")
        else:
            result_text = f"Unknown tool: {name}"
            logger.warning(f"[VAPI] Unknown tool requested: {name}")

    except Exception as e:
        logger.error(f"[VAPI] Error executing tool {name}: {e}", exc_info=True)
        result_text = f"An error occurred while executing {name}."

    logger.info(f"[VAPI] Returning result for {call_id}: {result_text[:200]}...")

    return {
        "results": [
            {
                "toolCallId": call_id,
                "result": result_text
            }
        ]
    }
