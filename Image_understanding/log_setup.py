import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


BASE_LOG_DIR = "/home/itel/Downloads/gemini/codes/uv_env/Image_understanding/logs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)


def _get_logger(name, filename):
    log_path = os.path.join(BASE_LOG_DIR, filename)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:  # Avoid duplicate handlers
        handler = RotatingFileHandler(
            log_path, maxBytes=5_000_000, backupCount=3
        )
        formatter = logging.Formatter("%(asctime)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


image_understanding_logger = _get_logger("image_understanding", "image_understanding.log")
multiple_image_logger = _get_logger("multiple_image", "multiple_image.log")
object_detection_logger = _get_logger("object_detection", "object_detection.log")
segmentation_logger = _get_logger("segmentation", "segmentation.log")
upload_image_logger = _get_logger("upload_image", "upload_image.log")
url_content_logger = _get_logger("url_content", "url_content.log")



# -----------------------------
#  Logging functions (API compatible)
# -----------------------------
def log(event_type, payload):
    event = {
        "time": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": payload
    }
    text_logger.info(json.dumps(event))
    print("log", event)


def image_understanding_log(event):
    image_understanding_logger.info(json.dumps(event))
    print("log", event)


def multiple_image_log(event):
    multiple_image_logger.info(json.dumps(event))
    print("log", event)


def object_detection_log(event):
    object_detection_logger.info(json.dumps(event))
    print("log", event)


def segmentation_log(event):
    segmentation_logger.info(json.dumps(event))
    print("log", event)


def upload_image_log(event):
    upload_image_logger.info(json.dumps(event))
    print("log", event)


def url_content_log(event):
    url_content_logger.info(json.dumps(event))
    print("log", event)


