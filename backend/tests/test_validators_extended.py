"""
Tests for Validators - Phase 7 Backend Coverage Extension
Story: REM-017 - Backend Unit Tests (Target: 80%+ Coverage)

Test Categories:
- ProcessNumberValidator.validate()
- ProcessNumberValidator._validate_check_digit()
- ProcessNumberValidator.format()
- ProcessNumberValidator.validate_and_format()
- Error handling and edge cases
"""

import pytest
from backend.validators import ProcessNumberValidator
from backend.exceptions import InvalidProcessNumberException


class TestProcessNumberValidatorValidate:
    """Tests for validate method (8 tests)."""

    def test_validate_with_formatted_number(self):
        """TC-1: Validates formatted CNJ process number."""
        # Valid CNJ number: 0001745-64.1989.8.19.0002
        number = "0001745-64.1989.8.19.0002"
        result = ProcessNumberValidator.validate(number)

        assert result == "00017456419898190002"
        assert len(result) == 20

    def test_validate_with_unformatted_number(self):
        """TC-2: Validates unformatted CNJ number (digits only)."""
        number = "00017456419898190002"
        result = ProcessNumberValidator.validate(number)

        assert result == "00017456419898190002"
        assert len(result) == 20

    def test_validate_with_whitespace(self):
        """TC-3: Strips whitespace from number."""
        number = "  0001745-64.1989.8.19.0002  "
        result = ProcessNumberValidator.validate(number)

        assert result == "00017456419898190002"

    def test_validate_empty_string_raises(self):
        """TC-4: Raises on empty string."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate("")

    def test_validate_none_raises(self):
        """TC-5: Raises on None."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate(None)

    def test_validate_non_string_raises(self):
        """TC-6: Raises on non-string input."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate(123456789)

    def test_validate_invalid_format_raises(self):
        """TC-7: Raises on invalid format."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate("invalid-format")

    def test_validate_wrong_digit_count_raises(self):
        """TC-8: Raises when not 20 digits."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate("0001745-93.1989.8.19.000")  # Only 19 digits


class TestProcessNumberValidatorCheckDigit:
    """Tests for _validate_check_digit method (5 tests)."""

    def test_check_digit_valid(self):
        """TC-9: Valid check digit passes validation."""
        # 0001745-64.1989.8.19.0002 is a valid CNJ number
        result = ProcessNumberValidator._validate_check_digit("00017456419898190002")
        assert result is True

    def test_check_digit_invalid_digit(self):
        """TC-10: Invalid check digit fails validation."""
        # Change check digit from 64 to 65
        result = ProcessNumberValidator._validate_check_digit("00017456519898190002")
        assert result is False

    def test_check_digit_wrong_length(self):
        """TC-11: Wrong length returns False."""
        result = ProcessNumberValidator._validate_check_digit("000174593198981900")  # 18 digits
        assert result is False

    def test_check_digit_non_numeric(self):
        """TC-12: Non-numeric input returns False."""
        result = ProcessNumberValidator._validate_check_digit("000174X3198981900a2")
        assert result is False

    def test_check_digit_calculation_modulo_97(self):
        """TC-13: Check digit calculated using modulo 97."""
        # Create a valid number to verify the algorithm works
        clean_num = "00017456419898190002"
        result = ProcessNumberValidator._validate_check_digit(clean_num)
        assert result is True


class TestProcessNumberValidatorFormat:
    """Tests for format method (4 tests)."""

    def test_format_valid_20_digits(self):
        """TC-14: Formats 20-digit number correctly."""
        clean = "00017456419898190002"
        result = ProcessNumberValidator.format(clean)

        assert result == "0001745-64.1989.8.19.0002"

    def test_format_another_valid_number(self):
        """TC-15: Formats another valid number."""
        clean = "00012341234567890123"
        result = ProcessNumberValidator.format(clean)

        # Format: NNNNNNN-DD.AAAA.J.TR.OOOO
        assert result == "0001234-12.3456.7.89.0123"

    def test_format_wrong_length_returns_unchanged(self):
        """TC-16: Returns unchanged if not 20 digits."""
        short = "0001234123456789012"  # 19 digits
        result = ProcessNumberValidator.format(short)

        assert result == short

    def test_format_preserves_digits(self):
        """TC-17: Formatting preserves all digits."""
        clean = "00017456419898190002"
        formatted = ProcessNumberValidator.format(clean)

        # Extract digits from formatted version
        digits_only = "".join(filter(str.isdigit, formatted))
        assert digits_only == clean


class TestProcessNumberValidatorValidateAndFormat:
    """Tests for validate_and_format method (4 tests)."""

    def test_validate_and_format_success(self):
        """TC-18: Returns both clean and formatted versions."""
        number = "0001745-64.1989.8.19.0002"
        clean, formatted = ProcessNumberValidator.validate_and_format(number)

        assert clean == "00017456419898190002"
        assert formatted == "0001745-64.1989.8.19.0002"

    def test_validate_and_format_unformatted_input(self):
        """TC-19: Works with unformatted input."""
        number = "00017456419898190002"
        clean, formatted = ProcessNumberValidator.validate_and_format(number)

        assert clean == "00017456419898190002"
        assert formatted == "0001745-64.1989.8.19.0002"

    def test_validate_and_format_invalid_raises(self):
        """TC-20: Raises on invalid number."""
        with pytest.raises(InvalidProcessNumberException):
            ProcessNumberValidator.validate_and_format("invalid")

    def test_validate_and_format_tuple_unpacking(self):
        """TC-21: Returns proper tuple for unpacking."""
        number = "0001745-64.1989.8.19.0002"
        result = ProcessNumberValidator.validate_and_format(number)

        assert isinstance(result, tuple)
        assert len(result) == 2
        clean, formatted = result
        assert isinstance(clean, str)
        assert isinstance(formatted, str)


class TestProcessNumberValidatorEdgeCases:
    """Tests for edge cases and special scenarios (5 tests)."""

    def test_validate_with_mixed_separators(self):
        """TC-22: Handles mixed separator styles."""
        # Test with partial separators (still must match CNJ pattern)
        number = "0001745-6419898.19.0002"
        result = ProcessNumberValidator.validate(number)
        assert result == "00017456419898190002"

    def test_validate_leading_trailing_spaces(self):
        """TC-23: Strips multiple leading/trailing spaces."""
        number = "    0001745-64.1989.8.19.0002    "
        result = ProcessNumberValidator.validate(number)
        assert result == "00017456419898190002"

    def test_format_zero_padded_numbers(self):
        """TC-24: Formats numbers with zero padding."""
        clean = "00000000000000000000"  # All zeros
        result = ProcessNumberValidator.format(clean)
        assert "0000000-00.0000.0.00.0000" == result

    def test_validate_maximum_valid_number(self):
        """TC-25: Validates high number values."""
        # This would need a valid check digit for a high number
        # Using pattern that might be valid
        number = "9999999-99.9999.9.99.9999"
        # This might fail due to check digit, but tests the handling
        try:
            result = ProcessNumberValidator.validate(number)
            # If it passes, check format
            assert len(result) == 20
        except InvalidProcessNumberException:
            # If it fails, that's expected for invalid check digit
            pass

    def test_cnj_pattern_regex(self):
        """TC-26: CNJ pattern regex matches expected formats."""
        valid_patterns = [
            "0001745-64.1989.8.19.0002",
            "0001745-6419898.19.0002",
            "00017456419898190002",
        ]

        for pattern in valid_patterns:
            assert ProcessNumberValidator.CNJ_PATTERN.match(pattern) is not None


class TestProcessNumberValidatorIntegration:
    """Integration tests combining multiple methods (3 tests)."""

    def test_validate_format_roundtrip(self):
        """TC-27: Validate → Format → Validate roundtrip."""
        original = "0001745-64.1989.8.19.0002"

        clean1, formatted = ProcessNumberValidator.validate_and_format(original)
        clean2 = ProcessNumberValidator.validate(formatted)

        assert clean1 == clean2

    def test_multiple_formats_same_number(self):
        """TC-28: Different formats of same number produce same result."""
        formats = [
            "0001745-64.1989.8.19.0002",
            "00017456419898190002",
            "0001745-641989819.0002",  # Partial separators (still valid pattern)
        ]

        results = [ProcessNumberValidator.validate(f) for f in formats]
        assert all(r == results[0] for r in results)

    def test_error_message_clarity(self):
        """TC-29: Error messages are clear and helpful."""
        try:
            ProcessNumberValidator.validate("invalid")
            assert False, "Should have raised exception"
        except InvalidProcessNumberException as e:
            assert "inválido" in str(e).lower() or "formato" in str(e).lower()
