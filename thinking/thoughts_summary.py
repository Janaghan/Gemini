import time
from google.genai import types
from config import client
from log_setup import log_thoughts_summary



def thoughts_summary(prompt):
    """Generate text using Gemini with thinking tokens enabled."""
    start_time = time.time()

    # Log request
    model = "gemini-2.5-pro"
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        # "timestamp": start_time
    }
    log_thoughts_summary(request_record)

    response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
        include_thoughts=True
        )
    )
    )

    for part in response.candidates[0].content.parts:
        if not part.text:
            continue
        if part.thought:
            print("Thought summary:")
            print(part.text)
            print()
        else:
            print("Answer:")
            print(part.text)
            print()
    end_time = time.time()
    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "latency_ms": round(end_time - start_time, 2),
    }
    log_thoughts_summary(response_record)

    return response.text


# Example usage
answer = thoughts_summary("What is the sum of the first 50 prime numbers?")
print("Answer", answer)
