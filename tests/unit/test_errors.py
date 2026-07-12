"""Unit tests for exception hierarchy."""

from __future__ import annotations

from app.utils.errors import AppError, DatabaseError, ValidationError


def test_app_error_message() -> None:
    err = AppError("boom", details={"code": 1})
    assert "boom" in str(err)
    assert err.details["code"] == 1


def test_hierarchy() -> None:
    assert issubclass(DatabaseError, AppError)
    assert issubclass(ValidationError, AppError)
