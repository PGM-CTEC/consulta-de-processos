"""
Tests for custom exceptions.
"""
import pytest
from exceptions import (
    ProcessNotFoundException,
    DataJudAPIException,
    InvalidProcessNumberException,
    DataIntegrityException,
    ValidationException,
)


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_process_not_found_exception(self):
        """Test ProcessNotFoundException."""
        exc = ProcessNotFoundException("12345678901234567890")
        assert "12345678901234567890" in str(exc)
        assert "não encontrado" in str(exc)

    def test_process_not_found_exception_no_number(self):
        """Test ProcessNotFoundException without process number."""
        exc = ProcessNotFoundException()
        assert "não encontrado" in str(exc)

    def test_datajud_api_exception(self):
        """Test DataJudAPIException."""
        exc = DataJudAPIException("Erro de conexão")
        assert "Erro de conexão" in str(exc)

    def test_datajud_api_exception_default(self):
        """Test DataJudAPIException with default message."""
        exc = DataJudAPIException()
        assert "DataJud" in str(exc)

    def test_invalid_process_number_exception(self):
        """Test InvalidProcessNumberException."""
        exc = InvalidProcessNumberException("Formato inválido")
        assert "Formato inválido" in str(exc)

    def test_data_integrity_exception(self):
        """Test DataIntegrityException."""
        exc = DataIntegrityException("Chave duplicada")
        assert "Chave duplicada" in str(exc)

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Campo obrigatório")
        assert "Campo obrigatório" in str(exc)

    def test_exceptions_are_subclass_of_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(ProcessNotFoundException, Exception)
        assert issubclass(DataJudAPIException, Exception)
        assert issubclass(InvalidProcessNumberException, Exception)
        assert issubclass(DataIntegrityException, Exception)
        assert issubclass(ValidationException, Exception)
