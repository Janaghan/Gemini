import json
import time
from google.genai import types           # correct import
from config import client                 # your Gemini client
from log_setup import log_thinking_level   # your logger

################## thinking level  ##################
######## NOT FREE ########
def thinking_level(prompt):

    start_time = time.time()

    model = "gemini-3-pro-preview"
    thinking_level="low"

    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        # "timestamp": time.time(),
    }
    log_thinking_level(request_record)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
        ),
    )
    # Log each streamed chunk
    response_record = {
        "event": "response",
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2),
    }

    end_time = time.time()

    log_thinking_level(response_record)

    return response.text


# Example usage
answer = thinking_level("Provide a list of 3 famous physicists and their key contributions")
print("Answer", answer)
