import json
import time

from google.genai import types
from config import client
from log_setup import log_sys_ins


def text_gen_with_sys(prompt):
    start_time = time.time()
    temperature = 0.1
    system_instruction= "You are a Math Teacher. Help students understand concepts."
    model = "gemini-2.5-flash"

    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "config": {
            "system_instruction": system_instruction,
            "temperature": temperature
        },
        "timestamp": time.time(),
    }
    log_sys_ins(request_record)

    # Build the actual request to Gemini
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature
        ),
        contents=prompt   
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    log_sys_ins(response_record)

    return response.text


# Run example
answer = text_gen_with_sys("How does AI work?")
print("\nFINAL ANSWER:\n", answer)
