import json
import time

from google.genai import Client, types  
from log_setup import log_thinking_budget
from config import client


def thinking_budget(prompt):
    start_time = time.time()

    thinking_budget=1024
    model = "gemini-2.5-pro"
    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        # "timestamp": time.time(),
    }
    log_thinking_budget(request_record)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024)
            # Turn off thinking:
            # thinking_config=types.ThinkingConfig(thinking_budget=0)
            # Turn on dynamic thinking:
            # thinking_config=types.ThinkingConfig(thinking_budget=-1)
        ),
    )
    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2),
        # "timestamp": time.time(),
    }
    log_thinking_budget(response_record)

    return response.text


# Example Usage
answer = thinking_budget("Provide a list of 3 famous physicists and their key contributions")

print("Answer", answer)
