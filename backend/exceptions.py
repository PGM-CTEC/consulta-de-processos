"""
Custom exception classes for the Consulta Processual API.
These exceptions provide clear, user-friendly error messages.
"""


class ProcessNotFoundException(Exception):
    """Raised when a process is not found in DataJud or local database."""

    def __init__(self, process_number: str = None):
        if process_number:
            self.message = f"Processo {process_number} não encontrado na base pública"
        else:
            self.message = "Processo não encontrado na base pública"
        super().__init__(self.message)


class DataJudAPIException(Exception):
    """Raised when DataJud API encounters an error."""

    def __init__(self, message: str = "Erro ao consultar a API DataJud"):
        self.message = message
        super().__init__(self.message)


class InvalidProcessNumberException(Exception):
    """Raised when a process number format is invalid."""

    def __init__(self, message: str = "Número do processo inválido"):
        self.message = message
        super().__init__(self.message)


class DataIntegrityException(Exception):
    """Raised when there's a data integrity issue in the database."""

    def __init__(self, message: str = "Erro de integridade nos dados"):
        self.message = message
        super().__init__(self.message)


class ValidationException(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Erro de validação"):
        self.message = message
        super().__init__(self.message)
