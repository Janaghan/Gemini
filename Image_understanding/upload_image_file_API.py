import time
from google.genai import types
from config import client
from log_setup import upload_image_log   # <-- updated name


def upload_image_file_API(file_path):

    start_time = time.time()

    # Log request
    request_record = {
            "event": "request",
            "input": file_path,
            "model": "gemini-2.5-flash",
        }
    upload_image_log(request_record)

    
    my_file = client.files.upload(file= file_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[my_file, "Caption this image."],
    )

    end_time = time.time()

    # Log response
    response_record = {
            "event": "response",
            "response_text": response.text,
            "latency_ms": round((end_time - start_time) , 2),
        }
    upload_image_log(response_record)




# Run example
upload_image_file_API("/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/images/images.png")
