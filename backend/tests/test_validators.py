"""
Tests for CNJ process number validation.
"""
import pytest
from validators import ProcessNumberValidator
from exceptions import InvalidProcessNumberException


class TestProcessNumberValidator:
    """Test suite for ProcessNumberValidator."""

    def test_valid_cnj_number_with_formatting(self):
        """Test validation of properly formatted CNJ number."""
        valid = "0001745-64.1989.8.19.0002"
        result = ProcessNumberValidator.validate(valid)
        assert result == "00017456419898190002"

    def test_valid_cnj_number_without_formatting(self):
        """Test validation of CNJ number without separators."""
        valid = "00017456419898190002"
        result = ProcessNumberValidator.validate(valid)
        assert result == "00017456419898190002"

    def test_invalid_format_too_short(self):
        """Test that short numbers are rejected."""
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate("123456")
        assert "Formato inválido" in str(exc_info.value)

    def test_invalid_format_wrong_pattern(self):
        """Test that incorrectly formatted numbers are rejected."""
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate("1234567-89-0123-4-56-7890")
        assert "Formato inválido" in str(exc_info.value)

    def test_invalid_check_digit(self):
        """Test that invalid check digit is detected."""
        # Same number but with wrong check digit (99 instead of 64)
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate("0001745-99.1989.8.19.0002")
        assert "dígito verificador incorreto" in str(exc_info.value)

    def test_empty_number(self):
        """Test that empty string is rejected."""
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate("")
        assert "obrigatório" in str(exc_info.value)

    def test_none_number(self):
        """Test that None is rejected."""
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate(None)
        assert "obrigatório" in str(exc_info.value)

    def test_format_clean_number(self):
        """Test formatting of 20-digit number."""
        clean = "00017456419898190002"
        formatted = ProcessNumberValidator.format(clean)
        assert formatted == "0001745-64.1989.8.19.0002"

    def test_validate_and_format(self):
        """Test combined validation and formatting."""
        input_number = "0001745-64.1989.8.19.0002"
        clean, formatted = ProcessNumberValidator.validate_and_format(input_number)
        assert clean == "00017456419898190002"
        assert formatted == "0001745-64.1989.8.19.0002"

    def test_number_with_spaces(self):
        """Test that numbers with spaces are handled."""
        with_spaces = "  0001745-64.1989.8.19.0002  "
        result = ProcessNumberValidator.validate(with_spaces)
        assert result == "00017456419898190002"

    def test_wrong_length_after_cleaning(self):
        """Test that numbers with wrong digit count are rejected."""
        with pytest.raises(InvalidProcessNumberException) as exc_info:
            ProcessNumberValidator.validate("0001745-64.1989.8.19.000")  # 19 digits
        # Fails at regex pattern check before length validation
        assert "Formato inválido" in str(exc_info.value)
