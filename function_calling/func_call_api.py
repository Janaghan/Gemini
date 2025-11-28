# ---------- Imports ----------
from log_setup import log_function_calling_api
from google.genai import types, Client
from config import client   
import time


schedule_meeting_function = {
    "name": "schedule_meeting",
    "description": "Schedules a meeting with specified attendees at a given time and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of people attending the meeting.",
            },
            "date": {
                "type": "string",
                "description": "Date of the meeting (e.g., '2024-07-29')",
            },
            "time": {
                "type": "string",
                "description": "Time of the meeting (e.g., '15:00')",
            },
            "topic": {
                "type": "string",
                "description": "The subject or topic of the meeting.",
            },
        },
        "required": ["attendees", "date", "time", "topic"],
    },
}
# ---------- Updated Function ----------
def function_call_api(prompt):
    model="gemini-2.5-flash"
    start_time = time.time()
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "timestamp": time.time(),
    }
    # Log request
    log_function_calling_api(request_record)


    tools = types.Tool(function_declarations=[schedule_meeting_function])
    config = types.GenerateContentConfig(tools=[tools])

    # Send request with function declarations
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )

    # Check for a function call
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")
        #  In a real app, you would call your function here:
        #  result = schedule_meeting(**function_call.args)
    else:
        print("No function call found in the response.")
        print(response.text)
    
    end_time = time.time()
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    # Log response
    log_function_calling_api(response_record)

    return response.text


function_call_api("Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about the Q3 planning.")
# print("Answer", answer)

