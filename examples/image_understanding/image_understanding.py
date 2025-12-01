# ---------- Imports ----------
from log_setup import image_understanding
from google.genai import types, Client
from config import client   


# ---------- Updated Function ----------
def generate_image(file_path):
    # Log request
    request_record = {
        "event": "request",
        "file_path": file_path,
        "model": "gemini-2.5-flash"
    }
    image_understanding_log(request_record)
    with open(file_path, 'rb') as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
        ),
        'Caption this image.'
        ]
    )
    # Log response
    response_record = {
        "event": "response",
        "file_path": file_path,
        "response_text": response.text,
        "model": "gemini-2.5-flash"
    }
    image_understanding_log(response_record)


if __name__ == "__main__":
    generate_image("/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/images/images.png")

