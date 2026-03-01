"""
Logging configuration for OpenWebUI Chat Client.
"""

import logging
import sys
from typing import Optional, Any

# Predefined format string
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(
    level: int = logging.INFO,
    fmt: str = DEFAULT_LOG_FORMAT,
    datefmt: Optional[str] = None,
    stream: Optional[Any] = None,
) -> None:
    """
    Apply a unified logging configuration targeting all 'openwebui_chat_client' loggers.

    Args:
        level: The logging level (e.g., logging.INFO, logging.DEBUG).
        fmt: The log format string.
        datefmt: The date format string.
        stream: Output stream (default is sys.stdout).
    """
    # Create the handler
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    # Configure the root logger for the library
    logger = logging.getLogger("openwebui_chat_client")
    logger.setLevel(level)

    # Avoid adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    # Prevent propagation to the root logger to avoid double logging
    # if the user has also configured the root logger.
    logger.propagate = False
