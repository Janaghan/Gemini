import json
import time
from PIL import Image

from google.genai import Client, types  
from log_setup import log_multimodal

from config import client


def multimodal_text_gen(prompt, image_path, system_instruction=None):
    start_time = time.time()

    # Load image
    image = Image.open(image_path)

    # --- Build config dynamically ---
    generation_config = {
        "system_instruction": system_instruction,
        "thinking_budget": -1,     # dynamic thinking
    }
    model = "gemini-2.5-flash"
    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "image_path": image_path,
        "model": model,
        "config": generation_config,
        # "timestamp": time.time(),
    }
    log_multimodal(request_record)

    # --- Build Gemini request ---
    contents = [image, prompt]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_budget=-1)
        ),
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "image_path": image_path,
        "response_text": response.text,
        "model": "gemini-2.5-flash",
        "latency_ms": round((end_time - start_time), 2),
        # "timestamp": time.time(),
    }
    log_multimodal(response_record)

    return response.text


# Example Usage
answer = multimodal_text_gen(
    prompt="Tell me about this instrument",
    image_path="/4TBHD/Janaghan/codes/frames/image.png",
    system_instruction="You are expert in describing images."
)

print("Answer", answer)
