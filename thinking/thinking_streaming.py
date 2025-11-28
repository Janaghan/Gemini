import json
import time

from google.genai import types
from config import client
from log_setup import log_thinking_streaming


def thinking_streaming(prompt):
    start_time = time.time()
    model = "gemini-2.5-pro"
    include_thoughts=True
    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "config": {
            "include_thoughts": include_thoughts
        },
        "timestamp": time.time(),
    }
    log_thinking_streaming(request_record)

    thoughts = ""
    answer = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            include_thoughts=include_thoughts
        )
        )
    ):
        for part in chunk.candidates[0].content.parts:
            if not part.text:
                continue
            elif part.thought:
                if not thoughts:
                    print("Thoughts summary:")
                print(part.text)
                thoughts += part.text
            else:
                if not answer:
                    print("Answer:")
                print(part.text)
                answer += part.text

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": answer,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    log_thinking_streaming(response_record)

    return answer


# Run example
prompt = """
Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.
The person who lives in the red house owns a cat.
Bob does not live in the green house.
Carol owns a dog.
The green house is to the left of the red house.
Alice does not own a cat.
Who lives in each house, and what pet do they own?
"""
answer = thinking_streaming(prompt)
print("\nFINAL ANSWER:\n", answer)
