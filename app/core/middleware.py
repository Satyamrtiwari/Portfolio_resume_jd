"""
Middleware for request tracing and timing.

- RequestIDMiddleware: Generates UUID4 per request, adds X-Request-ID header.
- TimingMiddleware: Measures request processing time, adds X-Process-Time header.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generates a unique request ID for every incoming request.

    The ID is:
    - Stored in ``request.state.request_id``
    - Added as ``X-Request-ID`` response header
    - Logged for traceability
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the request with a generated request ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(
            "[%s] %s %s",
            request_id[:8],
            request.method,
            request.url.path,
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Measures and logs request processing time.

    Adds ``X-Process-Time`` response header with elapsed time in seconds.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process the request and measure elapsed time."""
        start = time.perf_counter()

        response = await call_next(request)

        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.4f}"

        logger.debug(
            "%s %s completed in %.4f sec",
            request.method,
            request.url.path,
            elapsed,
        )

        return response
