"""Application logging with request IDs.

Sensitive medical data must never be logged at info level.
"""
import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    level = logging.DEBUG if not settings.is_production else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
