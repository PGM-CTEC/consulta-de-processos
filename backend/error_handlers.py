"""
Centralized error handlers for FastAPI application.
These handlers ensure user-friendly error messages while logging full details server-side.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import (
    ProcessNotFoundException,
    DataJudAPIException,
    InvalidProcessNumberException,
    DataIntegrityException,
    ValidationException,
)
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def process_not_found_handler(
    request: Request, exc: ProcessNotFoundException
) -> JSONResponse:
    """Handle process not found errors."""
    logger.info(f"Process not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def datajud_api_handler(
    request: Request, exc: DataJudAPIException
) -> JSONResponse:
    """Handle DataJud API errors."""
    logger.error(f"DataJud API Error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": exc.message or "Serviço temporariamente indisponível. Tente novamente."
        },
    )


async def validation_handler(
    request: Request, exc: InvalidProcessNumberException
) -> JSONResponse:
    """Handle process number validation errors."""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
    )


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Handle general validation errors."""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Erro de integridade nos dados. Por favor, tente novamente."},
    )


async def data_integrity_handler(
    request: Request, exc: DataIntegrityException
) -> JSONResponse:
    """Handle custom data integrity errors."""
    logger.error(f"Data integrity error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    Logs full error details server-side but returns sanitized message to user.
    """
    # Log full exception with stack trace
    logger.exception(
        f"Unhandled exception: {type(exc).__name__}",
        extra={"path": request.url.path, "method": request.method},
    )

    # Return generic error message to user
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor. Por favor, tente novamente mais tarde."
        },
    )


def register_exception_handlers(app):
    """
    Register all custom exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(ProcessNotFoundException, process_not_found_handler)
    app.add_exception_handler(DataJudAPIException, datajud_api_handler)
    app.add_exception_handler(
        InvalidProcessNumberException, validation_handler
    )
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(DataIntegrityException, data_integrity_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
