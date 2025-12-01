import json
import time
from google.genai import types           # correct import
from config import client                 # your Gemini client
from log_setup import log_streaming   # your logger


def generate_text_stream(prompt, system_instruction=None):
    """
    Streams text output from Gemini 2.5 Flash with chunk-level logging.
    """
    start_time = time.time()

    # Config payload for logs
    generation_config = {
        "system_instruction": system_instruction,
        "thinking_budget": -1,
    }
    model = "gemini-2.5-flash"


    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "model": model,
        "config": generation_config,
        # "timestamp": time.time(),
    }
    log_streaming(request_record)

    # Start streaming
    response_stream = client.models.generate_content_stream(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_budget=-1)
        ),
    )

    output = ""
    for chunk in response_stream:
        text = chunk.text 
        output += text


        # Log each streamed chunk
        chunk_record = {
            "event": "chunk_response",
            "chunk_text": text,
            "model": "gemini-2.5-flash",
            "timestamp": time.time(),
        }
        log_streaming(chunk_record)

        print(text, end="")  # live console output

    end_time = time.time()

    # Final response log
    response_record = {
        "event": "overall_response",
        "prompt": prompt,
        "response_text": output,
        "model": "gemini-2.5-flash",
        "latency_ms": round((end_time - start_time), 2),
        # "timestamp": time.time(),
    }
    log_streaming(response_record)

    return output


# Example usage
if __name__ == "__main__":

    answer = generate_text_stream("Explain how agentic AI works")
    print("Answer", answer)
