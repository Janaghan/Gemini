import time
from google.genai import types
from config import client
from log_setup import url_content_log
import requests


def url_content(image_path):
    """Generate text using Gemini with thinking tokens enabled."""
    start_time = time.time()

    # Log request
    request_record = {
        "event": "request",
        "image_path": image_path,
    }
    url_content_log(request_record)

    # Gemini API call
   
    image_bytes = requests.get(image_path).content
    image = types.Part.from_bytes(
      data=image_bytes, mime_type="image/jpeg"
    )

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=["What is this image?", image],
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "image_path": image_path,
        "response_text": response.text,
        "latency_ms": round(end_time - start_time, 2),
    }
    url_content_log(response_record)

    return response.text


# Example usage
answer = url_content("https://images.pexels.com/photos/1054655/pexels-photo-1054655.jpeg?cs=srgb&dl=pexels-hsapir-1054655.jpg&fm=jpg")
print("Answer", answer)

