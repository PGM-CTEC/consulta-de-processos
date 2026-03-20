"""
Tests for Custom Exceptions - Phase 5 Coverage Extension
Story: REM-017 - Backend Unit Tests (70% Coverage)

Test Categories:
- ProcessNotFoundException with and without process number
- DataJudAPIException with default and custom messages
- InvalidProcessNumberException with default and custom messages
- DataIntegrityException with default and custom messages
- ValidationException with default and custom messages
"""

from backend.exceptions import (
    ProcessNotFoundException,
    DataJudAPIException,
    InvalidProcessNumberException,
    DataIntegrityException,
    ValidationException
)


class TestProcessNotFoundException:
    """Tests for ProcessNotFoundException (2 tests)."""

    def test_process_not_found_with_number(self):
        """TC-1: ProcessNotFoundException with process number."""
        process_number = "0000001-01.0000.1.00.0001"
        exception = ProcessNotFoundException(process_number)

        assert exception.message == f"Processo {process_number} não encontrado na base pública"
        assert str(exception) == f"Processo {process_number} não encontrado na base pública"
        assert isinstance(exception, Exception)

    def test_process_not_found_without_number(self):
        """TC-2: ProcessNotFoundException without process number."""
        exception = ProcessNotFoundException()

        assert exception.message == "Processo não encontrado na base pública"
        assert str(exception) == "Processo não encontrado na base pública"


class TestDataJudAPIException:
    """Tests for DataJudAPIException (2 tests)."""

    def test_datajud_api_exception_default_message(self):
        """TC-3: DataJudAPIException with default message."""
        exception = DataJudAPIException()

        assert exception.message == "Erro ao consultar a API DataJud"
        assert str(exception) == "Erro ao consultar a API DataJud"
        assert isinstance(exception, Exception)

    def test_datajud_api_exception_custom_message(self):
        """TC-4: DataJudAPIException with custom message."""
        custom_message = "API timeout after 30 seconds"
        exception = DataJudAPIException(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message


class TestInvalidProcessNumberException:
    """Tests for InvalidProcessNumberException (2 tests)."""

    def test_invalid_process_number_default_message(self):
        """TC-5: InvalidProcessNumberException with default message."""
        exception = InvalidProcessNumberException()

        assert exception.message == "Número do processo inválido"
        assert str(exception) == "Número do processo inválido"
        assert isinstance(exception, Exception)

    def test_invalid_process_number_custom_message(self):
        """TC-6: InvalidProcessNumberException with custom message."""
        custom_message = "Expected format: NNNNNNN-DD.AAAA.J.TT.OOOO"
        exception = InvalidProcessNumberException(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message


class TestDataIntegrityException:
    """Tests for DataIntegrityException (2 tests)."""

    def test_data_integrity_exception_default_message(self):
        """TC-7: DataIntegrityException with default message."""
        exception = DataIntegrityException()

        assert exception.message == "Erro de integridade nos dados"
        assert str(exception) == "Erro de integridade nos dados"
        assert isinstance(exception, Exception)

    def test_data_integrity_exception_custom_message(self):
        """TC-8: DataIntegrityException with custom message."""
        custom_message = "Foreign key constraint violation: process_id not found"
        exception = DataIntegrityException(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message


class TestValidationException:
    """Tests for ValidationException (2 tests)."""

    def test_validation_exception_default_message(self):
        """TC-9: ValidationException with default message."""
        exception = ValidationException()

        assert exception.message == "Erro de validação"
        assert str(exception) == "Erro de validação"
        assert isinstance(exception, Exception)

    def test_validation_exception_custom_message(self):
        """TC-10: ValidationException with custom message."""
        custom_message = "Field 'tribunal_name' is required"
        exception = ValidationException(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message


class TestExceptionHierarchy:
    """Tests for exception hierarchy and catching (4 tests)."""

    def test_all_exceptions_inherit_from_exception(self):
        """TC-11: All custom exceptions inherit from Exception."""
        exceptions = [
            ProcessNotFoundException(),
            DataJudAPIException(),
            InvalidProcessNumberException(),
            DataIntegrityException(),
            ValidationException()
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)

    def test_process_not_found_is_exception(self):
        """TC-12: ProcessNotFoundException can be caught as Exception."""
        try:
            raise ProcessNotFoundException("0000001-01.0000.1.00.0001")
        except Exception as e:
            assert isinstance(e, ProcessNotFoundException)
            assert "não encontrado" in str(e)

    def test_datajud_exception_is_exception(self):
        """TC-13: DataJudAPIException can be caught as Exception."""
        try:
            raise DataJudAPIException("Connection timeout")
        except Exception as e:
            assert isinstance(e, DataJudAPIException)
            assert "Connection timeout" in str(e)

    def test_multiple_exception_types(self):
        """TC-14: Multiple exception types can be caught."""
        exceptions_to_test = [
            (ProcessNotFoundException("0000001-01.0000.1.00.0001"), ProcessNotFoundException),
            (InvalidProcessNumberException("Bad format"), InvalidProcessNumberException),
            (DataJudAPIException("API error"), DataJudAPIException),
        ]

        for exc, expected_type in exceptions_to_test:
            try:
                raise exc
            except expected_type as e:
                assert isinstance(e, Exception)
                assert len(e.message) > 0
