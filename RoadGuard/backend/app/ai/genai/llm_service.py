"""Configurable LLM client (OpenAI-compatible API).

When LLM_ENABLED=false (or no API key) the service degrades gracefully and the
application still works. The caller is told the output is templated, not LLM.
Never hard-code API keys.
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    def __init__(self) -> None:
        self.enabled = bool(settings.LLM_ENABLED and settings.LLM_API_KEY)
        self.client = None
        if self.enabled:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
            except ImportError:
                logger.warning("openai package not installed; LLM disabled")
                self.enabled = False

    @property
    def available(self) -> bool:
        return self.enabled and self.client is not None

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 700) -> dict:
        """Return {used_llm, text}."""
        if not self.available:
            return {"used_llm": False, "text": ""}
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            return {"used_llm": True, "text": response.choices[0].message.content or ""}
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM call failed: %s", exc)
            return {"used_llm": False, "text": ""}


llm_service = LLMService()


def sanitize(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove private fields before they can reach an LLM."""
    public = {k: v for k, v in payload.items()}
    for key in ("user_email", "user_phone", "email", "phone", "hashed_password"):
        public.pop(key, None)
    return public
