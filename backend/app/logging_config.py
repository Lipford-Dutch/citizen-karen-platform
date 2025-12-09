# backend/app/logging_config.py
import logging
import sys
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger("karing")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_logger():
    return logger
