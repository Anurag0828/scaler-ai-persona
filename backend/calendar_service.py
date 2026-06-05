import httpx
import logging
from datetime import datetime, timedelta
from .config import config

logger = logging.getLogger(__name__)

CAL_API_URL = "https://api.cal.com/v2"

async def get_available_slots(date: str, event_type_id: str = None) -> list:
    """
    Fetch available slots from Cal.com for a given date (YYYY-MM-DD).
    Returns a list of slots or an empty list on error.
    """
    if not config.CAL_API_KEY:
        logger.error("Cal.com API key is not configured.")
        return []
    
    # Use the configured event type ID, and extract only the digits in case a URL was pasted
    raw_event_id = event_type_id or config.CAL_EVENT_TYPE_ID
    if not raw_event_id:
        logger.error("CAL_EVENT_TYPE_ID is not configured. Cannot fetch slots.")
        return []
    
    import re
    match = re.search(r'(\d+)', str(raw_event_id))
    event_id = match.group(1) if match else str(raw_event_id)
    
    headers = {
        "Authorization": f"Bearer {config.CAL_API_KEY}",
        "cal-api-version": "2024-06-14"
    }
    
    try:
        # Calculate end date as the next day to get all slots for the requested date
        start_date = date
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            end_dt = dt + timedelta(days=1)
            end_date = end_dt.strftime("%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: {date}, using same day as end")
            end_date = date
        
        url = f"{CAL_API_URL}/slots?eventTypeId={event_id}&startTime={start_date}&endTime={end_date}&timeZone=Asia/Kolkata"
        
        logger.info(f"[CAL] Fetching slots: {url}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            
            logger.info(f"[CAL] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[CAL] Response data: {str(data)[:500]}")
                
                # Cal.com v2 returns slots nested under "data"
                if "data" in data:
                    slots_data = data["data"]
                    # Slots may be grouped by date
                    if isinstance(slots_data, dict):
                        all_slots = []
                        for day, day_slots in slots_data.items():
                            if isinstance(day_slots, list):
                                all_slots.extend(day_slots)
                        return all_slots
                    elif isinstance(slots_data, list):
                        return slots_data
                    return slots_data
                return data
            else:
                logger.error(f"[CAL] API error: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        logger.error(f"[CAL] Error fetching slots: {e}", exc_info=True)
        return []

async def book_meeting(name: str, email: str, start_time: str, event_type_id: str = None) -> dict:
    """
    Book a meeting on Cal.com.
    start_time should be ISO 8601 format.
    """
    if not config.CAL_API_KEY:
        return {"success": False, "error": "Cal.com API key is not configured."}
    
    raw_event_id = event_type_id or config.CAL_EVENT_TYPE_ID
    if not raw_event_id:
        return {"success": False, "error": "CAL_EVENT_TYPE_ID is not configured."}
    
    import re
    match = re.search(r'(\d+)', str(raw_event_id))
    event_id = match.group(1) if match else str(raw_event_id)
    
    headers = {
        "Authorization": f"Bearer {config.CAL_API_KEY}",
        "cal-api-version": "2024-06-14",
        "Content-Type": "application/json"
    }
    
    payload = {
        "start": start_time,
        "eventTypeId": int(event_id),
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": "Asia/Kolkata"
        },
        "metadata": {
            "notes": "Booked via AI Persona"
        }
    }
    
    logger.info(f"[CAL] Booking meeting: {json.dumps(payload)}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{CAL_API_URL}/bookings", headers=headers, json=payload)
            
            logger.info(f"[CAL] Booking response: {response.status_code} - {response.text[:500]}")
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                return {"success": True, "booking": data.get("data", data)}
            else:
                return {"success": False, "error": response.text}
    except Exception as e:
        logger.error(f"[CAL] Booking error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

# Need json import for booking payload logging
import json
