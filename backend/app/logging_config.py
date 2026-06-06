"""Logging configuration for the clinical trials API.

Call configure_logging() once at startup. Use get_logger(__name__) everywhere else.
Level is controlled by the LOG_LEVEL environment variable (default: INFO).
Logs are written to stdout and to logs/app.log (rotating, 10 MB × 5 files).
"""

import logging
import logging.handlers
import os
from pathlib import Path


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(console)
        root.addHandler(file_handler)
    else:
        root.handlers.clear()
        root.addHandler(console)
        root.addHandler(file_handler)

    # Suppress noisy third-party loggers unless we're in DEBUG mode
    if level > logging.DEBUG:
        for name in ("httpx", "httpcore", "litellm", "LiteLLM", "uvicorn.access"):
            logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
