"""Shared exception helpers."""
from fastapi import HTTPException


def not_found(message: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=404, detail=message)


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def forbidden(message: str = "You do not have permission for this action") -> HTTPException:
    return HTTPException(status_code=403, detail=message)


def unauthorized(message: str = "Not authenticated") -> HTTPException:
    return HTTPException(status_code=401, detail=message)
