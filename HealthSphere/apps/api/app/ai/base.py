"""AI provider abstraction.

The application never talks to a vendor SDK directly. Providers implement this
interface; selection is driven by the AI_PROVIDER setting.
"""
from dataclasses import dataclass, field
from typing import Optional, Protocol

from app.core.config import settings


@dataclass
class ExtractionResult:
    """Structured lab values extracted from report text."""
    entities: list[dict] = field(default_factory=list)
    document_type: str = "other"
    laboratory: Optional[str] = None
    report_date: Optional[str] = None
    confidence: float = 0.0


@dataclass
class AssistantReply:
    content: str
    safety_filtered: bool = False


class AIProvider(Protocol):
    name: str

    def extract_medical_data(self, text: str) -> ExtractionResult:
        """Extract structured lab values from report text."""
        ...

    def explain_report(self, context_json: str) -> str:
        """Plain-language explanation of an analyzed report (no diagnoses)."""
        ...

    def assistant_reply(self, question: str, health_context_json: str) -> AssistantReply:
        """Answer a user question using only the supplied authorized context."""
        ...


def get_ai_provider() -> AIProvider:
    from app.ai.providers.mock_provider import MockAIProvider

    if settings.ai_provider == "mock":
        return MockAIProvider()

    from app.ai.providers.openai_provider import OpenAIProvider

    return OpenAIProvider(
        api_key=settings.ai_api_key or "",
        base_url=settings.ai_base_url,
        model=settings.ai_model,
        compatible=settings.ai_provider == "openai_compatible",
    )
