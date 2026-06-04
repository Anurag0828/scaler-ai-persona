import httpx
from datetime import datetime
from .config import config

CAL_API_URL = "https://api.cal.com/v2"

async def get_available_slots(date: str, event_type_id: str = None) -> list:
    """
    Fetch available slots from Cal.com for a given date (YYYY-MM-DD).
    Returns a list of slots or an error string.
    """
    if not config.CAL_API_KEY:
        return "Error: Cal.com API key is not configured."
        
    # Default to 30 min meeting if not provided
    event_id = event_type_id or "10" # Using 10 as dummy/fallback
    
    headers = {
        "Authorization": f"Bearer {config.CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    
    # We fetch slots for the given day and the next day to ensure we have options
    try:
        # Simple date calculation just for string passing, in real app use datetime logic
        # For simplicity, we just pass start and end as the same date for now
        end_date = date 
        
        url = f"{CAL_API_URL}/slots?eventTypeId={event_id}&start={date}&end={end_date}&timeZone=Asia/Kolkata"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Slots usually come nested in data structure depending on API v2 response
                if "data" in data:
                    return data["data"]
                return data
            else:
                print(f"Cal.com API error: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        print(f"Error fetching slots: {e}")
        return []

async def book_meeting(name: str, email: str, start_time: str, event_type_id: str = None) -> dict:
    """
    Book a meeting on Cal.com.
    start_time should be ISO 8601 format.
    """
    if not config.CAL_API_KEY:
        return {"success": False, "error": "Cal.com API key is not configured."}
        
    event_id = event_type_id or 10 # Int for body
    
    headers = {
        "Authorization": f"Bearer {config.CAL_API_KEY}",
        "cal-api-version": "2024-09-04",
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{CAL_API_URL}/bookings", headers=headers, json=payload)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                return {"success": True, "booking": data.get("data", data)}
            else:
                return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
