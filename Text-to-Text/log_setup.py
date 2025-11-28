import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


BASE_LOG_DIR = "/home/itel/Downloads/gemini/codes/uv_env/Text-to-Text/logs"
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


text_logger = _get_logger("text_gen", "text_generation.log")
thinking_logger = _get_logger("thinking", "text_thinking.log")
system_logger = _get_logger("system", "text_sys_ins.log")
multimodal_logger = _get_logger("multimodal", "multimodal_input.log")
stream_logger = _get_logger("stream", "streaming.log")
multiturn_logger = _get_logger("multiturn", "multichat.log")


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


def log_thinking(event):
    thinking_logger.info(json.dumps(event))
    print("log", event)


def log_sys_ins(event):
    system_logger.info(json.dumps(event))
    print("log", event)


def log_multimodal(event):
    multimodal_logger.info(json.dumps(event))
    print("log", event)


def log_streaming(event):
    stream_logger.info(json.dumps(event))
    print("log", event)


def log_multichat(event):
    multiturn_logger.info(json.dumps(event))
    print("log", event)
