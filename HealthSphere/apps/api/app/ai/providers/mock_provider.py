"""Deterministic rule-based extraction provider.

Parses common lab report text patterns. It never invents reference ranges:
ranges are only captured when present in the document itself.
"""
import re
from datetime import datetime
from typing import Optional

from app.ai.base import AssistantReply, ExtractionResult

# test_name -> (aliases, typical units)  Units are used for normalization only.
TEST_PATTERNS: list[tuple[str, list[str]]] = [
    ("HbA1c", [r"hba1c", r"glycated\s*haemoglobin", r"glycosylated\s*haemoglobin"]),
    ("Fasting Blood Glucose", [r"fasting\s*blood\s*(glucose|sugar)", r"fbs", r"glucose\s*\(?\s*fasting"]),
    ("Post Prandial Blood Glucose", [r"post\s*prandial", r"pp\s*blood\s*(glucose|sugar)", r"\bppbs\b"]),
    ("Total Cholesterol", [r"total\s*cholesterol"]),
    ("LDL Cholesterol", [r"ldl[\s\-]*cholesterol", r"\bldl\b"]),
    ("HDL Cholesterol", [r"hdl[\s\-]*cholesterol", r"\bhdl\b"]),
    ("Triglycerides", [r"triglycerides"]),
    ("Hemoglobin", [r"haemoglobin\b", r"hemoglobin\b", r"\bhgb\b", r"\bhb\b(?!\w)"]),
    ("WBC Count", [r"total\s*leucocyte\s*count", r"wbc\s*count", r"\btlc\b", r"\bwbc\b"]),
    ("Platelet Count", [r"platelet\s*count", r"\bplatelets\b"]),
    ("TSH", [r"\btsh\b", r"thyroid\s*stimulating\s*hormone"]),
    ("Serum Creatinine", [r"serum\s*creatinine", r"\bcreatinine\b"]),
    ("Blood Urea", [r"blood\s*urea", r"\burea\b"]),
    ("SGPT (ALT)", [r"\bsgpt\b", r"\balt\b", r"alanine\s*transaminase"]),
    ("SGOT (AST)", [r"\bsgot\b", r"\bast\b", r"aspartate\s*transaminase"]),
    ("Vitamin D", [r"vitamin\s*d", r"25[\s\-]*oh\s*vitamin\s*d"]),
    ("Vitamin B12", [r"vitamin\s*b12"]),
]

_NUM = r"([0-9]+(?:[.,][0-9]+)?)"
_UNIT_MAP = {"mg/dl": "mg/dL", "mg%": "mg/dL", "g/dl": "g/dL", "gm%": "g/dL", "%": "%",
             "mmol/l": "mmol/L", "iu/ml": "IU/mL", "uiu/ml": "µIU/mL", "ng/ml": "ng/mL",
             "pg/ml": "pg/mL", "/ul": "/µL", "cells/cumm": "cells/µL", "10^3/ul": "10³/µL",
             "ug/dl": "µg/dL", "ng/dl": "ng/dL"}


class MockAIProvider:
    name = "mock"

    def extract_medical_data(self, text: str) -> ExtractionResult:
        entities: list[dict] = []
        lab_name = self._extract_laboratory(text)
        report_date = self._extract_date(text)
        doc_type = self._classify(text)

        lines = re.split(r"[\n\r]+", text)
        for line in lines:
            if not line or len(line) > 300:
                continue
            match = self._parse_line(line)
            if match:
                entities.append(match)

        confidence = 0.9 if entities else 0.0
        return ExtractionResult(
            entities=entities,
            document_type=doc_type,
            laboratory=lab_name,
            report_date=report_date,
            confidence=confidence,
        )

    def _parse_line(self, line: str) -> Optional[dict]:
        lowered = line.lower()
        for test_name, patterns in TEST_PATTERNS:
            for pattern in patterns:
                m = re.search(pattern, lowered)
                if not m:
                    continue
                value_m = re.search(_NUM + r"\s*([a-zA-Zµ%^/\.0-9]*)", line[m.end():])
                if not value_m:
                    return None
                raw_value = value_m.group(1).replace(",", ".")
                try:
                    value = float(raw_value)
                except ValueError:
                    return None
                unit_raw = (value_m.group(2) or "").strip().lower()
                unit = _UNIT_MAP.get(unit_raw, unit_raw or None)

                ref_low, ref_high = self._extract_reference(line)
                abnormal = False
                if ref_low is not None and value < ref_low:
                    abnormal = True
                if ref_high is not None and value > ref_high:
                    abnormal = True

                return {
                    "test_name": test_name,
                    "value": value,
                    "unit": unit,
                    "reference_low": ref_low,
                    "reference_high": ref_high,
                    "abnormal_flag": abnormal,
                    "confidence": 0.92,
                    "source_text": line.strip()[:200],
                }
        return None

    @staticmethod
    def _extract_reference(line: str) -> tuple[Optional[float], Optional[float]]:
        # Patterns like "(4.0 - 6.0)", "Reference: 70-100 mg/dL", "4.0 to 6.0 %"
        m = re.search(
            r"(?:ref(?:erence)?(?:\s*range)?\s*[:\-]?\s*)?[(\[]?\s*"
            r"([0-9]+(?:[.,][0-9]+)?)\s*(?:-|–|to)\s*([0-9]+(?:[.,][0-9]+)?)\s*[)\]]?",
            line.lower(),
        )
        if not m:
            return None, None
        try:
            low = float(m.group(1).replace(",", "."))
            high = float(m.group(2).replace(",", "."))
            if low > high:
                return None, None
            return low, high
        except ValueError:
            return None, None

    @staticmethod
    def _extract_laboratory(text: str) -> Optional[str]:
        m = re.search(r"(?:lab(?:oratory)?|pathology|diagnostics)\s*[:\-]\s*([^\n]{2,80})", text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    @staticmethod
    def _extract_date(text: str) -> Optional[str]:
        m = re.search(
            r"(?:reported?|collected)?\s*date\s*[:\-]?\s*([0-9]{1,4}[-/.][0-9]{1,2}[-/.][0-9]{1,4})",
            text, re.IGNORECASE,
        )
        if not m:
            return None
        raw = m.group(1)
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    @staticmethod
    def _classify(text: str) -> str:
        lowered = text.lower()
        category_scores = [
            ("lipid_profile", ["cholesterol", "triglyceride", "hdl", "ldl"]),
            ("hba1c", ["hba1c"]),
            ("blood_glucose", ["glucose", "blood sugar"]),
            ("thyroid", ["tsh", "t3", "t4", "thyroid"]),
            ("liver_function", ["sgpt", "sgot", "bilirubin", "liver"]),
            ("kidney_function", ["creatinine", "urea", "kidney"]),
            ("cbc", ["hemoglobin", "platelet", "leucocyte", "wbc", "rbc"]),
        ]
        best, best_score = "other", 0
        for cat, keywords in category_scores:
            score = sum(lowered.count(k) for k in keywords)
            if score > best_score:
                best, best_score = cat, score
        return best

    def explain_report(self, context_json: str) -> str:
        import json

        ctx = json.loads(context_json)
        flagged = ctx.get("flagged_results", [])
        if not flagged:
            return (
                "All extracted values appear within the reference ranges shown on the "
                "report. This summary is informational and not a medical assessment."
            )
        names = ", ".join(f"{f['test_name']} ({f['value']}{f.get('unit') or ''})" for f in flagged)
        return (
            f"The following results appear outside the reference ranges printed on your "
            f"report: {names}. Values outside a reference range are common and do not by "
            f"themselves indicate a condition — many factors can affect a single reading. "
            f"This may be worth discussing with your healthcare professional."
        )

    def assistant_reply(self, question: str, health_context_json: str) -> AssistantReply:
        import json

        ctx = json.loads(health_context_json)
        parts: list[str] = []
        latest = ctx.get("latest_report")
        if latest:
            parts.append(
                f"Your most recent report ({latest['date']}, {latest['category'].replace('_', ' ')}) "
                f"contains {latest['result_count']} extracted result(s)."
            )
        trends = ctx.get("trends", [])
        for t in trends[:3]:
            direction = t["direction"]
            phrase = {
                "increasing": "has been increasing",
                "decreasing": "has been decreasing",
                "stable": "has stayed stable",
                "insufficient_data": "does not have enough history to show a trend yet",
                "sudden_change": "shows a sudden change",
            }.get(direction, direction)
            parts.append(f"{t['metric'].replace('_', ' ')} {phrase} across your records.")
        reminders = ctx.get("upcoming_reminders", [])
        if reminders:
            titles = ", ".join(r["title"] for r in reminders[:3])
            parts.append(f"Upcoming reminders: {titles}.")
        suggestions = ctx.get("specialist_suggestions", [])
        for s in suggestions[:3]:
            parts.append(
                f"Specialist suggestion on record: {s['specialty']} ({s['relevance']} "
                f"relevance). Reason on record: {s['reason_on_record']} This came from "
                f"the Specialist Engine — it may be appropriate to discuss this "
                f"suggestion with a qualified healthcare professional."
            )

        if parts:
            content = " ".join(parts) + (
                "\n\nRemember: I can help you review your own records, but I cannot "
                "diagnose conditions or advise on medications. Please discuss any concerns "
                "with a qualified healthcare professional."
            )
        else:
            content = (
                "I don't have relevant information in your records for that question yet. "
                "You can upload reports or add health measurements, then ask me again. "
                "I cannot diagnose conditions or provide medical advice."
            )
        return AssistantReply(content=content)
