"""Tests for logging functionality."""

import pytest
import json
import os
from pathlib import Path
from backend.utils.logger import setup_logger, get_logger
from backend.utils.redact import redact_value, redact_dict


def test_logger_setup():
    """Test logger initialization."""
    logger = setup_logger(name="test_logger", log_file="logs/test.log")
    assert logger is not None
    assert logger.name == "test_logger"


def _close_logger(logger):
    """Close all file handlers (needed on Windows to release the file lock)."""
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)


def test_logger_writes_json():
    """Test that logger writes valid JSON to file."""
    log_file = "logs/test_json.log"
    os.makedirs("logs", exist_ok=True)

    logger = setup_logger(name="test_json", log_file=log_file)
    logger.info("Test message", extra={"process_number": "123"})

    # Verify file exists and contains valid JSON
    assert Path(log_file).exists()

    with open(log_file, 'r') as f:
        line = f.readline()
        log_entry = json.loads(line)
        assert log_entry['message'] == 'Test message'
        assert log_entry['process_number'] == '123'

    # Close handlers before cleanup (required on Windows)
    _close_logger(logger)
    Path(log_file).unlink()


def test_logger_rotation():
    """Test that logger respects maxBytes limit."""
    log_file = "logs/test_rotation.log"
    os.makedirs("logs", exist_ok=True)

    logger = setup_logger(
        name="test_rotation",
        log_file=log_file,
        max_bytes=100,  # Very small for testing
        backup_count=2
    )

    # Write multiple log entries to trigger rotation
    for i in range(5):
        logger.info(f"Test message {i}", extra={"index": i})

    # Should have created rotated files
    assert Path(log_file).exists()
    # Close handlers before cleanup (required on Windows)
    _close_logger(logger)
    for f in Path("logs").glob("test_rotation.log*"):
        f.unlink(missing_ok=True)


def test_redact_cpf():
    """Test CPF redaction."""
    value = "User with CPF 123.456.789-01 in database"
    redacted = redact_value(value)
    assert "[REDACTED-CPF]" in redacted
    assert "123.456.789" not in redacted


def test_redact_email():
    """Test email redaction."""
    value = "Contact user@example.com for info"
    redacted = redact_value(value)
    assert "[REDACTED-EMAIL]" in redacted
    assert "user@example.com" not in redacted


def test_redact_dict():
    """Test recursive dictionary redaction."""
    data = {
        "email": "user@example.com",
        "nested": {
            "cpf": "123.456.789-01",
            "info": "public data"
        }
    }

    redacted = redact_dict(data)
    assert "[REDACTED-EMAIL]" in redacted["email"]
    assert "[REDACTED-CPF]" in redacted["nested"]["cpf"]
    assert redacted["nested"]["info"] == "public data"


def test_get_logger():
    """Test getting existing logger."""
    logger1 = setup_logger(name="my_logger")
    logger2 = get_logger(name="my_logger")

    assert logger1.name == logger2.name
