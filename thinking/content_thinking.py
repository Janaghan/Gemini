# ---------- Imports ----------
from log_setup import log_content_thinking
from google.genai import types, Client
from config import client   
import time

# ---------- Updated Function ----------
def content_thinking(prompt):
    model="gemini-2.5-pro"
    start_time = time.time()
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "timestamp": time.time(),
    }
    # Log request
    log_content_thinking(request_record)

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    end_time = time.time()
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    # Log response
    log_content_thinking(response_record)

    return response.text


answer = content_thinking("Explain the concept of Occam's Razor and provide a simple, everyday example.")
print("Answer", answer)

