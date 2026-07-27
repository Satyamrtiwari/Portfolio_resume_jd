"""
Global exception handlers.

Registers handlers for:
- Custom application exceptions (AppException hierarchy)
- FastAPI RequestValidationError
- Unhandled exceptions (500)

All responses follow a consistent JSON format with the error detail
and request ID (when available).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle custom application exceptions."""
        request_id = getattr(request.state, "request_id", None)

        logger.error(
            "[%s] AppException: %s (status=%d)",
            (request_id or "unknown")[:8],
            exc.detail,
            exc.status_code,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": request_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic / FastAPI validation errors."""
        request_id = getattr(request.state, "request_id", None)

        # Build a human-readable error message
        errors = exc.errors()
        messages = []
        for error in errors:
            loc = " → ".join(str(l) for l in error.get("loc", []))
            msg = error.get("msg", "Unknown error")
            messages.append(f"{loc}: {msg}")

        detail = "; ".join(messages) if messages else "Validation error"

        logger.warning(
            "[%s] Validation error: %s",
            (request_id or "unknown")[:8],
            detail,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": detail,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle all unhandled exceptions with a generic 500 response."""
        request_id = getattr(request.state, "request_id", None)

        logger.exception(
            "[%s] Unhandled exception: %s",
            (request_id or "unknown")[:8],
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred. Please try again later.",
                "request_id": request_id,
            },
        )
