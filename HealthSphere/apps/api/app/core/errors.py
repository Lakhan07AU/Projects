"""Consistent API error responses.

Every error returns:
{"success": false, "error": {"code": "...", "message": "..."}}
Stack traces are never exposed to clients.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("healthsphere")


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "You do not have access to this resource"):
        super().__init__("FORBIDDEN", message, status.HTTP_403_FORBIDDEN)


class RateLimitError(AppError):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__("RATE_LIMITED", message, status.HTTP_429_TOO_MANY_REQUESTS)


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return error_response(exc.code, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        first = exc.errors()[0] if exc.errors() else {}
        loc = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        msg = first.get("msg", "Invalid input")
        message = f"Invalid value for '{loc}': {msg}" if loc else msg
        return error_response("VALIDATION_ERROR", message, status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error")
        return error_response(
            "DATABASE_ERROR",
            "A database error occurred. Please try again.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        return error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
