"""OpenAI-compatible LLM provider (works with OpenAI, Azure-style gateways, local
servers exposing an OpenAI API such as Ollama/vLLM via base_url).

The LLM is used ONLY to structure extracted text and explain deterministic
results. It never invents clinical rules — those live in the rule engine.
Output is validated; malformed output is rejected and the system falls back.
"""
import json
import logging
from typing import Optional

from app.ai.base import AssistantReply, ExtractionResult

logger = logging.getLogger("healthsphere.ai")

SYSTEM_EXTRACTION = """You are a medical document data extraction service.
Extract lab test values from the given report text into JSON:
{"entities": [{"test_name": str, "value": number, "unit": str|null,
"reference_low": number|null, "reference_high": number|null}],
 "document_type": one of [cbc, lipid_profile, hba1c, blood_glucose, thyroid,
 liver_function, kidney_function, ecg, imaging, prescription, doctor_note, other],
 "laboratory": str|null, "report_date": "YYYY-MM-DD"|null}
Rules:
- Only extract values actually present in the text. Never invent or estimate values.
- If no reference range is printed for a test, set reference_low/high to null. NEVER guess ranges.
- Ignore narrative text, addresses, doctor names.
- Respond with ONLY the JSON object."""

SYSTEM_EXPLAIN = """You are a careful health-report explainer for a wellness app.
Explain the provided analyzed results in plain language for a general audience.
STRICT SAFETY RULES:
- Never diagnose any condition. Never mention specific diseases as conclusions.
- Never advise starting/stopping/changing medication.
- Use phrases like "appears outside the reference range shown on the report",
  "may be worth discussing with your healthcare professional".
- Keep under 180 words. No markdown headers."""

SYSTEM_ASSISTANT = """You are HealthSphere assistant, a personal health records helper.
Answer ONLY using the user's health context provided. If the context lacks the answer,
say so honestly. You may summarize trends and suggest what topics could be worth
discussing with a healthcare professional. STRICT RULES: never diagnose, never
prescribe or comment on medication changes, never claim certainty about future
health. Keep answers concise and kind. No markdown headers."""


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, base_url: Optional[str], model: str, compatible: bool = False):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url or None)
        self.model = model
        self.compatible = compatible

    def _chat(self, system: str, user: str, json_mode: bool = False) -> str:
        kwargs = {}
        if json_mode and not self.compatible:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=1200,
            **kwargs,
        )
        return (resp.choices[0].message.content or "").strip()

    def extract_medical_data(self, text: str) -> ExtractionResult:
        raw = self._chat(SYSTEM_EXTRACTION, text[:15000], json_mode=True)
        try:
            data = json.loads(raw)
            entities = []
            for e in data.get("entities", []):
                value = float(e["value"])
                ref_low = e.get("reference_low")
                ref_high = e.get("reference_high")
                abnormal = False
                if ref_low is not None and value < float(ref_low):
                    abnormal = True
                if ref_high is not None and value > float(ref_high):
                    abnormal = True
                entities.append({
                    "test_name": str(e["test_name"])[:255],
                    "value": value,
                    "unit": e.get("unit"),
                    "reference_low": float(ref_low) if ref_low is not None else None,
                    "reference_high": float(ref_high) if ref_high is not None else None,
                    "abnormal_flag": abnormal,
                    "confidence": 0.85,
                })
            return ExtractionResult(
                entities=entities,
                document_type=data.get("document_type", "other"),
                laboratory=data.get("laboratory"),
                report_date=data.get("report_date"),
                confidence=0.85 if entities else 0.0,
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            logger.warning("LLM extraction produced invalid output: %s", exc)
            # Fall back to deterministic parser rather than failing outright
            from app.ai.providers.mock_provider import MockAIProvider

            return MockAIProvider().extract_medical_data(text)

    def explain_report(self, context_json: str) -> str:
        return self._chat(SYSTEM_EXPLAIN, context_json[:6000])

    def assistant_reply(self, question: str, health_context_json: str) -> AssistantReply:
        content = self._chat(
            SYSTEM_ASSISTANT,
            f"User's authorized health context:\n{health_context_json[:6000]}\n\nQuestion: {question}",
        )
        return AssistantReply(content=content)
