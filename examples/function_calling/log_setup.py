import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


BASE_LOG_DIR = "/home/itel/Downloads/gemini/codes/uv_env/function_calling/logs"
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

automatic_function_calling_logger = _get_logger("automatic_function_calling", "automatic_function_calling.log")
composite_function_calling_logger = _get_logger("composite_function_calling", "composite_function_calling.log")
function_calling_api_logger = _get_logger("function_calling_api", "function_calling_api.log")
function_calling_logger = _get_logger("function_calling", "function_calling.log")
parallel_function_calling_logger = _get_logger("parallel_function_calling", "parallel_function_calling.log")

# -----------------------------
#  Logging functions (API compatible)
# -----------------------------


def log_automatic_function_calling(event):
    automatic_function_calling_logger.info(json.dumps(event))
    print("log", event)


def log_composite_function_calling(event):
    composite_function_calling_logger.info(json.dumps(event))
    print("log", event)


def log_function_calling_api(event):
    function_calling_api_logger.info(json.dumps(event))
    print("log", event)


def log_function_calling(event):
    function_calling_logger.info(json.dumps(event))
    print("log", event)


def log_parallel_function_calling(event):
    parallel_function_calling_logger.info(json.dumps(event))
    print("log", event)
