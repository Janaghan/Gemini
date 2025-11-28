import json
import time
from PIL import Image

from google.genai import Client, types  
from log_setup import object_detection_log

from config import client


def multimodal_text_gen(image_path):
    start_time = time.time()
    prompt = "Detect the all of the prominent items in the image. The box_2d should be [ymin, xmin, ymax, xmax] normalized to 0-1000."

    # Log request
    request_record = {
        "event": "request",
        "prompt": prompt,
        "image_path": image_path,
    }
    object_detection_log(request_record)


    image = Image.open(image_path)

    config = types.GenerateContentConfig(
    response_mime_type="application/json"
    )

    response = client.models.generate_content(model="gemini-2.5-flash",
                                            contents=[image, prompt],
                                            config=config
                                            )

    width, height = image.size
    bounding_boxes = json.loads(response.text)

    converted_bounding_boxes = []
    for bounding_box in bounding_boxes:
        abs_y1 = int(bounding_box["box_2d"][0]/1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1]/1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2]/1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3]/1000 * width)
        converted_bounding_boxes.append([abs_x1, abs_y1, abs_x2, abs_y2])

    print("Image size: ", width, height)
    print("Bounding boxes:", converted_bounding_boxes)

    end_time = time.time()

    # Log response
    response_record = {
        "event": "response",
        "prompt": prompt,
        "image_path": image_path,
        "response_text": response.text,
        "latency_ms": round((end_time - start_time), 2),
        # "timestamp": time.time(),
    }
    object_detection_log(response_record)

    return response.text


# Example Usage
object_detect = multimodal_text_gen(
    image_path="/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/images/generate_image_light.png",
)

print( object_detect)
