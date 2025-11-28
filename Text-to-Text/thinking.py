import time
from google.genai import types
from config import client
from log_setup import log_thinking



def generate_text_with_thinking(prompt):
    """Generate text using Gemini with thinking tokens enabled."""
    start_time = time.time()

    # Log request
    thinking_budget = 0
    model = "gemini-2.5-flash"
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "config": thinking_budget,
        # "timestamp": start_time
    }
    log_thinking(request_record)

    # Gemini API call
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
        ),
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round(end_time - start_time, 2),
        # "timestamp": end_time
    }
    log_thinking(response_record)

    return response.text


# Example usage
answer = generate_text_with_thinking("How does AI work?")
print("Answer", answer)
