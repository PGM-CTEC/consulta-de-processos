"""
Tests for Error Handlers - Phase 6 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage Target)

Test Categories:
- ProcessNotFoundException handler
- DataJudAPIException handler
- InvalidProcessNumberException handler
- ValidationException handler
- IntegrityError handler
- DataIntegrityException handler
- Generic exception handler
- Handler registration
"""

import asyncio
from unittest.mock import MagicMock
from fastapi import FastAPI, status
from sqlalchemy.exc import IntegrityError

from backend.error_handlers import (
    process_not_found_handler,
    datajud_api_handler,
    validation_handler,
    validation_exception_handler,
    integrity_error_handler,
    data_integrity_handler,
    generic_exception_handler,
    register_exception_handlers,
)
from backend.exceptions import (
    ProcessNotFoundException,
    DataJudAPIException,
    InvalidProcessNumberException,
    ValidationException,
    DataIntegrityException,
)


class TestProcessNotFoundHandler:
    """Tests for process not found error handler (2 tests)."""

    def test_process_not_found_handler_response(self):
        """TC-1: ProcessNotFoundException handler returns 404."""
        request = MagicMock()
        exc = ProcessNotFoundException("0000001-01.0000.1.00.0001")

        response = asyncio.run(process_not_found_handler(request, exc))

        assert response.status_code == 404

    def test_process_not_found_handler_default_message(self):
        """TC-2: ProcessNotFoundException handler with default message."""
        request = MagicMock()
        exc = ProcessNotFoundException()

        response = asyncio.run(process_not_found_handler(request, exc))

        assert response.status_code == 404


class TestDataJudAPIHandler:
    """Tests for DataJud API error handler (2 tests)."""

    def test_datajud_api_handler_response(self):
        """TC-3: DataJudAPIException handler returns 503."""
        request = MagicMock()
        exc = DataJudAPIException("API timeout")

        response = asyncio.run(datajud_api_handler(request, exc))

        assert response.status_code == 503
        assert "API timeout" in str(response.body)

    def test_datajud_api_handler_default_message(self):
        """TC-4: DataJudAPIException handler with default message."""
        request = MagicMock()
        exc = DataJudAPIException()

        response = asyncio.run(datajud_api_handler(request, exc))

        assert response.status_code == 503
        assert "Erro ao consultar a API DataJud" in str(response.body)


class TestValidationHandler:
    """Tests for validation error handler (1 test)."""

    def test_validation_handler_response(self):
        """TC-5: InvalidProcessNumberException handler returns 400."""
        request = MagicMock()
        exc = InvalidProcessNumberException("Invalid format")

        response = asyncio.run(validation_handler(request, exc))

        assert response.status_code == 400
        assert "Invalid format" in str(response.body)


class TestValidationExceptionHandler:
    """Tests for general validation exception handler (1 test)."""

    def test_validation_exception_handler_response(self):
        """TC-6: ValidationException handler returns 400."""
        request = MagicMock()
        exc = ValidationException("Field required")

        response = asyncio.run(validation_exception_handler(request, exc))

        assert response.status_code == 400
        assert "Field required" in str(response.body)


class TestIntegrityErrorHandler:
    """Tests for database integrity error handler (1 test)."""

    def test_integrity_error_handler_response(self):
        """TC-7: IntegrityError handler returns 409."""
        request = MagicMock()
        # Create a mock IntegrityError
        exc = MagicMock(spec=IntegrityError)
        exc.__str__ = MagicMock(return_value="Foreign key violation")

        response = asyncio.run(integrity_error_handler(request, exc))

        assert response.status_code == 409
        assert "integridade" in str(response.body).lower()


class TestDataIntegrityHandler:
    """Tests for custom data integrity error handler (1 test)."""

    def test_data_integrity_handler_response(self):
        """TC-8: DataIntegrityException handler returns 409."""
        request = MagicMock()
        exc = DataIntegrityException("Constraint violation")

        response = asyncio.run(data_integrity_handler(request, exc))

        assert response.status_code == 409
        assert "Constraint violation" in str(response.body)


class TestGenericExceptionHandler:
    """Tests for generic exception handler (2 tests)."""

    def test_generic_exception_handler_response(self):
        """TC-9: Generic exception handler returns 500."""
        request = MagicMock()
        request.url.path = "/api/test"
        request.method = "GET"
        exc = Exception("Unexpected error")

        response = asyncio.run(generic_exception_handler(request, exc))

        assert response.status_code == 500

    def test_generic_exception_handler_sanitized_message(self):
        """TC-10: Generic exception handler returns generic message."""
        request = MagicMock()
        request.url.path = "/api/test"
        request.method = "POST"
        exc = ValueError("Sensitive information")

        response = asyncio.run(generic_exception_handler(request, exc))

        # Should return generic message, not the sensitive one
        assert response.status_code == 500
        assert "tente novamente" in str(response.body).lower()


class TestRegisterExceptionHandlers:
    """Tests for exception handler registration (2 tests)."""

    def test_register_exception_handlers_adds_handlers(self):
        """TC-11: register_exception_handlers registers all handlers."""
        app = FastAPI()

        # Before registration, exception_handlers should be minimal
        initial_count = len(app.exception_handlers)

        register_exception_handlers(app)

        # After registration, should have 7 handlers
        final_count = len(app.exception_handlers)
        assert final_count > initial_count

    def test_register_exception_handlers_all_exceptions(self):
        """TC-12: All custom exceptions are registered."""
        app = FastAPI()
        register_exception_handlers(app)

        # Verify key exception handlers are registered
        assert ProcessNotFoundException in app.exception_handlers
        assert DataJudAPIException in app.exception_handlers
        assert InvalidProcessNumberException in app.exception_handlers
        assert ValidationException in app.exception_handlers
        assert DataIntegrityException in app.exception_handlers
        assert Exception in app.exception_handlers


class TestErrorHandlerStatusCodes:
    """Tests for correct HTTP status codes (3 tests)."""

    def test_404_for_not_found(self):
        """TC-13: Not found errors return 404."""
        request = MagicMock()
        exc = ProcessNotFoundException("test")

        response = asyncio.run(process_not_found_handler(request, exc))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_400_for_validation(self):
        """TC-14: Validation errors return 400."""
        request = MagicMock()
        exc = InvalidProcessNumberException("test")

        response = asyncio.run(validation_handler(request, exc))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_503_for_api_errors(self):
        """TC-15: API errors return 503."""
        request = MagicMock()
        exc = DataJudAPIException("test")

        response = asyncio.run(datajud_api_handler(request, exc))

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
