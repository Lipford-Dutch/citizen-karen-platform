# backend/app/logging_config.py
import logging
import sys
import json_log_formatter


def _configure_logger(name: str = "karing") -> logging.Logger:
    formatter = json_log_formatter.JSONFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    log = logging.getLogger(name)
    if not log.handlers:
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False
    return log


logger = _configure_logger()


def get_logger() -> logging.Logger:
    return logger
