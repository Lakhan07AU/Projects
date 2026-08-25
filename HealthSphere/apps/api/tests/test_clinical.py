"""Clinical rule engine + AI safety tests."""
from app.clinical.rules import evaluate_rules, evaluate_trigger


class FakeRule:
    def __init__(self, key, trigger, priority="low", enabled=True):
        from app.models import Priority

        self.rule_key = key
        self.trigger = trigger
        self.enabled = enabled
        self.priority = Priority(priority)


CTX = {
    "age": 45,
    "family_condition_keywords": ["type 2 diabetes", "hypertension"],
    "flagged_test_keywords": ["ldl cholesterol"],
    "latest_blood_pressure_systolic": 150.0,
}


def test_rule_fires_on_family_history_and_age():
    rule = FakeRule("r1", {"all_of": [{"fact": "age", "gte": 35},
                                       {"fact": "family_condition_keywords", "value": ["diabet"]}]})
    assert evaluate_trigger(rule.trigger, CTX) is True


def test_rule_blocked_by_age():
    rule = FakeRule("r2", {"all_of": [{"fact": "age", "gte": 65}]})
    assert evaluate_trigger(rule.trigger, CTX) is False


def test_missing_fact_fails_safe():
    rule = FakeRule("r3", {"all_of": [{"fact": "nonexistent_fact", "gte": 10}]})
    assert evaluate_trigger(rule.trigger, CTX) is False


def test_malformed_rule_does_not_fire():
    assert evaluate_trigger({"all_of": [{"fact": "age", "gte": "not-a-number"}]}, CTX) is False
    assert evaluate_trigger({}, CTX) is False


def test_any_of_group():
    rule = FakeRule(
        "r4",
        {"any_of": [{"fact": "age", "gte": 80}, {"fact": "latest_blood_pressure_systolic", "gte": 140}]},
    )
    assert evaluate_trigger(rule.trigger, CTX) is True


def test_priority_ordering():
    rules = [
        FakeRule("low", {"all_of": [{"fact": "age", "gte": 18}]}, priority="low"),
        FakeRule("high", {"all_of": [{"fact": "age", "gte": 18}]}, priority="high"),
        FakeRule("med", {"all_of": [{"fact": "age", "gte": 18}]}, priority="medium"),
    ]
    fired = evaluate_rules(rules, CTX)
    assert [r.rule_key for r in fired] == ["high", "med", "low"]


def test_disabled_rule_skipped():
    rule = FakeRule("off", {"all_of": [{"fact": "age", "gte": 18}]}, enabled=False)
    assert evaluate_rules([rule], CTX) == []


# ---- AI output safety validation ----
def test_safety_validator_blocks_diagnostic_language():
    from app.services.pipeline import safety_validate

    unsafe = "Based on your HbA1c, you have diabetes and should stop taking your medicine."
    safe_text = safety_validate(unsafe)
    assert "you have diabetes" not in safe_text.lower()
    assert "stop taking" not in safe_text.lower()


def test_safety_validator_passes_cautious_language():
    from app.services.pipeline import safety_validate

    cautious = (
        "Your result appears outside the reference range shown on the report. "
        "This may be worth discussing with your healthcare professional."
    )
    assert safety_validate(cautious) == cautious
