"""JSON Logger configuration for FastAPI."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logger(
    name: str = "backend",
    log_file: str = "logs/backend.log",
    max_bytes: int = 10_000_000,  # 10MB
    backup_count: int = 7,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configure JSON logger with rotating file handler.

    Args:
        name: Logger name
        log_file: Path to log file
        max_bytes: Max size per file (10MB default)
        backup_count: Number of backup files to keep
        level: Logging level

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplication
    logger.handlers.clear()

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_handler.setLevel(level)

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(process_number)s %(tribunal)s %(path)s %(method)s'
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "backend") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
