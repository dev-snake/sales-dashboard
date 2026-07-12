"""Application exception hierarchy.

Business code in later phases should raise these types instead of bare Exception.
"""

from __future__ import annotations


class AppError(Exception):
    """Base error for all application-domain failures."""

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class ConfigError(AppError):
    """Invalid or missing configuration."""


class DatabaseError(AppError):
    """Database connectivity or persistence failures."""


class ValidationError(AppError):
    """Input / schema / business validation failures."""


class ETLError(AppError):
    """Extract-Transform-Load pipeline failures."""


class ReportError(AppError):
    """Report generation failures."""


class NotFoundError(AppError):
    """Requested entity was not found."""
