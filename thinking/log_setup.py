import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


BASE_LOG_DIR = "/home/itel/Downloads/gemini/codes/uv_env/thinking/logs"
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

content_thinking_logger = _get_logger("content_thinking", "content_thinking.log")
thinking_budget_logger = _get_logger("thinking_budget", "thinking_budget.log")
thinking_level_logger = _get_logger("thinking_level", "thinking_level.log")
thinking_streaming_logger = _get_logger("thinking_streaming", "thinking_streaming.log")
thoughts_summary_logger = _get_logger("thoughts_summary", "thoughts_summary.log")

# -----------------------------
#  Logging functions (API compatible)
# -----------------------------


def log_content_thinking(event):
    content_thinking_logger.info(json.dumps(event))
    print("log", event)


def log_thinking_budget(event):
    thinking_budget_logger.info(json.dumps(event))
    print("log", event)


def log_thinking_level(event):
    thinking_level_logger.info(json.dumps(event))
    print("log", event)


def log_thinking_streaming(event):
    thinking_streaming_logger.info(json.dumps(event))
    print("log", event)


def log_thoughts_summary(event):
    thoughts_summary_logger.info(json.dumps(event))
    print("log", event)
