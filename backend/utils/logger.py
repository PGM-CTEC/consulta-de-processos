"""JSON Logger configuration for FastAPI.

Story: REM-016 — Centralized Logging (Local)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

# JSON format fields for backend application log
_APP_FORMAT = (
    "%(timestamp)s %(level)s %(name)s %(message)s "
    "%(process_number)s %(tribunal)s %(path)s %(method)s"
)

# JSON format fields for HTTP access log
_ACCESS_FORMAT = (
    "%(timestamp)s %(level)s %(name)s %(message)s "
    "%(method)s %(path)s %(status_code)s %(duration_ms)s "
    "%(client_ip)s %(correlation_id)s"
)


def _make_rotating_handler(
    log_file: str,
    max_bytes: int,
    backup_count: int,
    level: int,
    fmt: str,
) -> RotatingFileHandler:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    handler.setLevel(level)
    handler.setFormatter(jsonlogger.JsonFormatter(fmt))
    return handler


def setup_logger(
    name: str = "backend",
    log_file: str = "logs/backend.log",
    max_bytes: int = 10_000_000,  # 10 MB
    backup_count: int = 7,
    level: int = logging.DEBUG,
    console: bool = False,
) -> logging.Logger:
    """
    Configure JSON logger with rotating file handler.

    Args:
        name:         Logger name
        log_file:     Path to log file (directory is created automatically)
        max_bytes:    Max size per file before rotation (default 10 MB)
        backup_count: Number of rotated files to keep
        level:        Logging level
        console:      Also write to stdout (useful for development)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    logger.addHandler(
        _make_rotating_handler(log_file, max_bytes, backup_count, level, _APP_FORMAT)
    )

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(jsonlogger.JsonFormatter(_APP_FORMAT))
        logger.addHandler(console_handler)

    return logger


def setup_access_logger(
    log_file: str = "logs/access.log",
    max_bytes: int = 10_000_000,  # 10 MB
    backup_count: int = 7,
) -> logging.Logger:
    """
    Configure a dedicated HTTP access logger.

    Logs one JSON line per request (written by RequestLoggerMiddleware).

    Returns:
        Configured access logger instance
    """
    logger = logging.getLogger("access")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.addHandler(
        _make_rotating_handler(
            log_file, max_bytes, backup_count, logging.DEBUG, _ACCESS_FORMAT
        )
    )
    return logger


def get_logger(name: str = "backend") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
