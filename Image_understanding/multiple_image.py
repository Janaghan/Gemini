import json
import time

from google.genai import types
from config import client
from log_setup import multiple_image_log


def multiple_image(image1_path, image2_path):
    start_time = time.time()

    model = "gemini-2.5-flash"

    # Log request
    request_record = {
        "event": "request",
        "image1_path": image1_path,
        "image2_path": image2_path,
        "model": model
    }
    multiple_image_log(request_record)

    # Upload the first image
    uploaded_file = client.files.upload(file=image1_path)

    # Prepare the second image as inline data
    with open(image2_path, 'rb') as f:
        img2_bytes = f.read()

    # Create the prompt with text and multiple images
    response = client.models.generate_content(

        model="gemini-2.5-flash",
        contents=[
            "What is different between these two images?",
            uploaded_file,  # Use the uploaded file reference
            types.Part.from_bytes(
                data=img2_bytes,
                mime_type='image/png'
            )
        ]
    )

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "image1_path": image1_path,
        "image2_path": image2_path,
        "response_text": response.text,
        "model": model,
        "latency_ms": round((end_time - start_time), 2)
    }
    multiple_image_log(response_record)

    return response.text


# Run example
answer = multiple_image("/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/images/generate_image_light.png", "/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/images/images.png")
print("\nFINAL ANSWER:\n", answer)
