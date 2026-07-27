"""
FastAPI dependency injection functions.

All services are initialized during the lifespan startup and stored
in app.state. These functions retrieve them for route injection.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import Request

from app.services.matching_service import MatchingService

# Module-level references set by main.py lifespan
_matching_service: MatchingService | None = None
_startup_time: datetime | None = None


def set_matching_service(service: MatchingService) -> None:
    """Set the global matching service reference (called during lifespan startup)."""
    global _matching_service
    _matching_service = service


def set_startup_time(time: datetime) -> None:
    """Set the startup time (called during lifespan startup)."""
    global _startup_time
    _startup_time = time


def get_matching_service() -> MatchingService:
    """
    Return the matching service instance.

    Used as a FastAPI Depends() dependency.

    Returns:
        The initialized MatchingService.

    Raises:
        RuntimeError: If the service has not been initialized.
    """
    if _matching_service is None:
        raise RuntimeError("MatchingService has not been initialized.")
    return _matching_service


def get_startup_time() -> datetime:
    """
    Return the application startup time.

    Used for uptime calculation in the health endpoint.

    Returns:
        The datetime when the application started.

    Raises:
        RuntimeError: If startup time has not been set.
    """
    if _startup_time is None:
        raise RuntimeError("Startup time has not been set.")
    return _startup_time
