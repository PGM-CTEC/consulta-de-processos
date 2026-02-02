"""
Validation utilities for CNJ process numbers and other inputs.
"""
import re
from exceptions import InvalidProcessNumberException


class ProcessNumberValidator:
    """
    Validates CNJ process numbers according to Resolution CNJ No. 65/2008.

    CNJ Format: NNNNNNN-DD.AAAA.J.TR.OOOO
    Where:
    - NNNNNNN: Sequential number (7 digits)
    - DD: Check digits (2 digits) - calculated using modulo 97
    - AAAA: Year of registration (4 digits)
    - J: Judicial segment (1 digit) - 1 to 9
    - TR: Court (2 digits) - 01 to 90
    - OOOO: Origin (4 digits)
    """

    # Regex pattern for CNJ format (with or without separators)
    CNJ_PATTERN = re.compile(r"^\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}\.?\d{4}$")

    @classmethod
    def validate(cls, number: str) -> str:
        """
        Validates and normalizes CNJ process number.

        Args:
            number: Process number string (can include formatting)

        Returns:
            str: Cleaned process number (digits only, 20 characters)

        Raises:
            InvalidProcessNumberException: If validation fails
        """
        if not number or not isinstance(number, str):
            raise InvalidProcessNumberException("Número do processo é obrigatório")

        # Remove whitespace
        number = number.strip()

        # Check format
        if not cls.CNJ_PATTERN.match(number):
            raise InvalidProcessNumberException(
                "Formato inválido. Use: NNNNNNN-DD.AAAA.J.TR.OOOO (Ex: 0001745-93.1989.8.19.0002)"
            )

        # Extract only digits
        clean = "".join(filter(str.isdigit, number))

        # Must be exactly 20 digits
        if len(clean) != 20:
            raise InvalidProcessNumberException(
                f"Número do processo deve conter exatamente 20 dígitos (recebido: {len(clean)})"
            )

        # Validate check digit
        if not cls._validate_check_digit(clean):
            raise InvalidProcessNumberException(
                "Número do processo inválido (dígito verificador incorreto)"
            )

        return clean

    @staticmethod
    def _validate_check_digit(clean: str) -> bool:
        """
        Validates CNJ check digit using modulo 97 algorithm.

        CNJ Format: NNNNNNN DD AAAA J TR OOOO
        Check digit (DD) is at positions 7-8 (0-indexed)

        Algorithm:
        1. Remove check digit from number
        2. Calculate: remainder = number % 97
        3. Check digit = 98 - remainder

        Args:
            clean: 20-digit process number

        Returns:
            bool: True if check digit is valid
        """
        if len(clean) != 20:
            return False

        # Extract check digit (positions 7-8)
        check_digit = int(clean[7:9])

        # Build number without check digit: NNNNNNN + AAAA + J + TR + OOOO
        origin = clean[:7]  # NNNNNNN
        year = clean[9:13]  # AAAA
        segment = clean[13]  # J
        court = clean[14:16]  # TR
        origin_code = clean[16:20]  # OOOO

        # Concatenate in the order specified by CNJ
        number_without_check = origin + year + segment + court + origin_code

        try:
            # Calculate expected check digit
            remainder = int(number_without_check) % 97
            expected_check = 98 - remainder

            return check_digit == expected_check
        except ValueError:
            return False

    @classmethod
    def format(cls, number: str) -> str:
        """
        Formats clean number to CNJ standard with separators.

        Args:
            number: 20-digit process number

        Returns:
            str: Formatted number (NNNNNNN-DD.AAAA.J.TR.OOOO)
        """
        if len(number) != 20:
            return number

        return (
            f"{number[0:7]}-{number[7:9]}.{number[9:13]}."
            f"{number[13]}.{number[14:16]}.{number[16:20]}"
        )

    @classmethod
    def validate_and_format(cls, number: str) -> tuple[str, str]:
        """
        Validates and returns both clean and formatted versions.

        Args:
            number: Process number to validate

        Returns:
            tuple: (clean_number, formatted_number)

        Raises:
            InvalidProcessNumberException: If validation fails
        """
        clean = cls.validate(number)
        formatted = cls.format(clean)
        return clean, formatted
