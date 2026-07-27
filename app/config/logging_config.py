"""
Structured logging configuration.

Configures Python's logging module with a consistent format including
timestamps, log level, module name, and request ID (when available).
"""

import logging
import sys

from app.config.settings import get_settings


def setup_logging() -> None:
    """
    Configure application-wide logging.

    Sets up a StreamHandler writing to stdout with a structured format.
    Log level is read from the application settings.
    """
    settings = get_settings()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Reset root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL.upper())
    console_handler.setFormatter(
        logging.Formatter(fmt=log_format, datefmt=date_format)
    )

    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger for the given module.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
