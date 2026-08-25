"""Validated clinical knowledge seeds.

IMPORTANT: These rules are general, population-level guidance drawn from
publicly available screening guidance. They are decision-SUPPORT topics for
discussion with a qualified professional — never automated diagnoses or
prescriptions. Each rule carries source + version + review-date metadata.
"""
from app.models import ClinicalRule, ClinicalSource

CLINICAL_SOURCES = [
    {
        "key": "ada-standards-2025",
        "title": "Standards of Care in Diabetes (screening topics overview)",
        "publisher": "American Diabetes Association",
        "version": "2025",
        "publication_date": "2025-01",
        "last_reviewed": "2026-01",
        "jurisdiction": "general",
        "url": None,
    },
    {
        "key": "uspstf-hypertension-2021",
        "title": "Screening for Hypertension in Adults",
        "publisher": "US Preventive Services Task Force",
        "version": "2021",
        "publication_date": "2021-04",
        "last_reviewed": "2026-01",
        "jurisdiction": "general",
        "url": None,
    },
    {
        "key": "who-physical-activity-2020",
        "title": "WHO Guidelines on Physical Activity and Sedentary Behaviour",
        "publisher": "World Health Organization",
        "version": "2020",
        "publication_date": "2020-11",
        "last_reviewed": "2026-01",
        "jurisdiction": "global",
        "url": None,
    },
    {
        "key": "who-healthy-diet-2020",
        "title": "Healthy Diet Fact Sheet",
        "publisher": "World Health Organization",
        "version": "2020",
        "publication_date": "2020-04",
        "last_reviewed": "2026-01",
        "jurisdiction": "global",
        "url": None,
    },
    {
        "key": "nih-vitamind-2021",
        "title": "Vitamin D Deficiency in Adults (background information)",
        "publisher": "NIH Office of Dietary Supplements",
        "version": "2021",
        "publication_date": "2021",
        "last_reviewed": "2026-01",
        "jurisdiction": "general",
        "url": None,
    },
]

# Trigger DSL evaluated by app.clinical.rules.evaluate_trigger()
CLINICAL_RULES = [
    {
        "rule_key": "glucose-family-history-screening",
        "condition": "blood_sugar_context",
        "population": "adults_35_plus_with_family_history",
        "trigger": {
            "all_of": [
                {"fact": "age", "gte": 35},
                {"fact": "family_condition_keywords", "value": ["diabet"]},
            ]
        },
        "recommendation": (
            "Consider discussing blood-sugar screening (such as HbA1c or fasting glucose) "
            "with your healthcare professional, since your records include a family history "
            "of diabetes-related conditions."
        ),
        "explanation": (
            "Family history is one factor professionals consider when personalizing "
            "screening discussions. This is not a diagnosis or a test prescription."
        ),
        "source_key": "ada-standards-2025",
        "priority": "medium",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "bp-high-recent-measurement",
        "condition": "cardiovascular_health",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "latest_blood_pressure_systolic", "gte": 140}]},
        "recommendation": (
            "Your recorded blood pressure appears elevated compared with values commonly "
            "used as a general guide. Blood pressure can vary between readings — consider "
            "measuring again when rested and discussing your readings with a healthcare "
            "professional."
        ),
        "explanation": (
            "Single readings may be affected by stress, caffeine, or measurement technique. "
            "Professionals confirm elevated blood pressure across multiple readings."
        ),
        "source_key": "uspstf-hypertension-2021",
        "priority": "high",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "ldl-above-reference",
        "condition": "cholesterol_context",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "flagged_test_keywords", "value": ["ldl"]}]},
        "recommendation": (
            "Your latest lipid panel includes an LDL value outside the reference range shown "
            "on that report. Consider discussing these results with your healthcare "
            "professional before making any changes."
        ),
        "explanation": (
            "LDL interpretation depends on overall cardiovascular context which only a "
            "qualified professional can assess."
        ),
        "source_key": "uspstf-hypertension-2021",
        "priority": "medium",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "anemia-flag-followup",
        "condition": "blood_health",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "flagged_test_keywords", "value": ["hemoglobin"]}]},
        "recommendation": (
            "Your latest CBC shows a hemoglobin value outside the printed reference range. "
            "This may be worth discussing with your healthcare professional, especially if "
            "you have felt unusually tired."
        ),
        "explanation": (
            "Hemoglobin varies with many factors including hydration and altitude; only a "
            "professional can interpret it in context."
        ),
        "source_key": "ada-standards-2025",
        "priority": "medium",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "thyroid-flag-followup",
        "condition": "thyroid_context",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "flagged_test_keywords", "value": ["tsh"]}]},
        "recommendation": (
            "Your thyroid-related result appears outside the reference range on the report. "
            "Consider sharing this result with your healthcare professional."
        ),
        "explanation": "Thyroid results are interpreted alongside clinical findings.",
        "source_key": "ada-standards-2025",
        "priority": "low",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "vitamin-d-low-flag",
        "condition": "bone_health",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "flagged_test_keywords", "value": ["vitamin d"]}]},
        "recommendation": (
            "A vitamin D result on your latest report appears below the printed reference "
            "range. Vitamin D levels vary seasonally — consider discussing this with a "
            "healthcare professional before starting supplements."
        ),
        "explanation": "Supplement decisions should involve a qualified professional.",
        "source_key": "nih-vitamind-2021",
        "priority": "low",
        "last_reviewed": "2026-01",
    },
    {
        "rule_key": "adult-bp-periodic-discussion",
        "condition": "general_preventive",
        "population": "adults",
        "trigger": {"all_of": [{"fact": "age", "gte": 18}]},
        "recommendation": (
            "Consider periodic blood-pressure checks as part of routine preventive care, "
            "and discuss an appropriate schedule with your healthcare professional."
        ),
        "explanation": "General population-level guidance; individual schedules vary.",
        "source_key": "uspstf-hypertension-2021",
        "priority": "low",
        "last_reviewed": "2026-01",
    },
]


def seed_clinical_knowledge(db) -> None:
    """Idempotently insert sources + rules."""
    existing_sources = {s.key for s in db.query(ClinicalSource).all()}
    for src in CLINICAL_SOURCES:
        if src["key"] not in existing_sources:
            db.add(ClinicalSource(**src))
    db.flush()  # ensure sources exist before rules reference them

    existing_rules = {r.rule_key for r in db.query(ClinicalRule).all()}
    for rule in CLINICAL_RULES:
        if rule["rule_key"] not in existing_rules:
            db.add(ClinicalRule(**rule))
    db.commit()
