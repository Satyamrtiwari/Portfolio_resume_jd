"""
Custom exception classes for the application.

Each exception carries an HTTP status code and detail message,
enabling the global exception handler to return consistent error responses.
"""

from fastapi import status


class AppException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class FileParsingError(AppException):
    """Raised when a PDF or uploaded file cannot be parsed."""

    def __init__(self, detail: str = "Failed to parse the uploaded file.") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnsupportedFileTypeError(AppException):
    """Raised when the uploaded file type is not supported."""

    def __init__(self, detail: str = "Unsupported file type. Only PDF files are accepted.") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class EmptyDocumentError(AppException):
    """Raised when the provided document contains no extractable text."""

    def __init__(self, detail: str = "The document is empty or contains no extractable text.") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ModelLoadError(AppException):
    """Raised when the embedding model fails to load."""

    def __init__(self, detail: str = "Failed to load the embedding model.") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class FileSizeExceededError(AppException):
    """Raised when the uploaded file exceeds the maximum allowed size."""

    def __init__(self, detail: str = "File size exceeds the maximum allowed limit.") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
