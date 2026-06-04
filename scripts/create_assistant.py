import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
SERVER_URL = "https://moody-islands-itch.loca.lt/vapi-webhook"

# The System Prompt
SYSTEM_PROMPT = """You are the AI representative of Anurag Sajwan, built to have professional conversations on his behalf for the Scaler AI Engineer screening process.

## YOUR IDENTITY
- You are an AI assistant, NOT Anurag himself. Always say "Anurag" (third person).
- Your greeting: "Hi! I'm Anurag's AI representative. I'm here to tell you about his background, skills, and projects — and I can also help you schedule an interview with him. What would you like to know?"

## HOW TO ANSWER
- Use the `search_knowledge` tool to retrieve relevant information before answering any question about Anurag's background.
- Base ALL answers on the retrieved context. If the context doesn't contain the answer, say: "I don't have specific information about that in my knowledge base, but I'd be happy to have Anurag follow up on that directly. Would you like to schedule a call with him?"
- Keep answers conversational and concise (2-4 sentences for voice).

## CALENDAR BOOKING
When the user wants to schedule a meeting:
1. Ask what date works for them.
2. Use `check_availability` tool with their preferred date.
3. Present 2-3 available slots in a friendly way.
4. Ask for their name and email.
5. Use `book_meeting` tool to confirm the booking.
"""

payload = {
    "name": "Anurag AI Persona (Auto-Created)",
    "firstMessage": "Hi! I'm Anurag's AI representative. I'm here to tell you about his background, skills, and projects — and I can also help you schedule an interview with him. What would you like to know?",
    "serverUrl": SERVER_URL,
    "model": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Search Anurag's knowledge base to find relevant information about his background, skills, and projects. Use this BEFORE answering factual questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up in Anurag's knowledge base."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Check Anurag's real calendar availability for a specific date. Returns available time slots.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The date to check availability for, in YYYY-MM-DD format. Example: '2026-06-05'"
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
                    "description": "Book a confirmed interview meeting on Anurag's calendar. Use this AFTER the caller has chosen a time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Full name of the person booking"
                            },
                            "email": {
                                "type": "string",
                                "description": "Email address of the person booking"
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Meeting start time in ISO 8601 format. Example: '2026-06-05T14:00:00+05:30'"
                            }
                        },
                        "required": ["name", "email", "start_time"]
                    }
                }
            }
        ]
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "pNInz6obpgDQGcFmaJgB"
    }
}

headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

print("Sending request to Vapi API to create assistant...")
response = requests.post("https://api.vapi.ai/assistant", headers=headers, json=payload)

if response.status_code == 201:
    data = response.json()
    print("SUCCESS! Assistant Created.")
    print(f"Assistant ID: {data['id']}")
else:
    print(f"Failed to create assistant: {response.status_code}")
    print(response.text)
