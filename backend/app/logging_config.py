"""Logging configuration for the clinical trials API.

Call configure_logging() once at startup. Use get_logger(__name__) everywhere else.
Level is controlled by the LOG_LEVEL environment variable (default: INFO).
Logs are written to stdout and to logs/app.log (rotating, 10 MB × 5 files).
"""

import logging
import logging.handlers
from pathlib import Path

# Third-party loggers that produce noise at any level.  Always capped at WARNING
# so real errors still surface but debug/info chatter is silenced.
_SILENT_LOGGERS = (
    "httpcore",
    "httpx",
    "botocore",
    "aiobotocore",
    "s3transfer",
    "urllib3",
    "litellm",
    "LiteLLM",
    "uvicorn.access",
)


class _AppFormatter(logging.Formatter):
    """Strip the 'app.' package prefix from logger names for readability."""

    def format(self, record: logging.LogRecord) -> str:
        # Avoid mutating the shared LogRecord; clone the name temporarily.
        original_name = record.name
        record.name = record.name.removeprefix("app.")
        result = super().format(record)
        record.name = original_name
        return result


def configure_logging() -> None:
    from app.config import settings  # local import — keeps get_logger() import-safe everywhere

    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = _AppFormatter(
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
    root.handlers.clear()
    root.addHandler(console)
    root.addHandler(file_handler)

    # Always suppress third-party noise regardless of LOG_LEVEL.
    for name in _SILENT_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
