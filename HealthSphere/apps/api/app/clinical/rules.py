"""Declarative rule trigger evaluation.

Triggers are JSON predicates evaluated against a user's HealthContext dict.
The LLM never defines rules — it can only explain results of fired rules.
"""
from app.models import ClinicalRule


def _match_predicate(pred: dict, ctx: dict) -> bool:
    fact = ctx.get(pred["fact"])
    if fact is None:
        return False
    if "gte" in pred:
        return float(fact) >= float(pred["gte"])
    if "lte" in pred:
        return float(fact) <= float(pred["lte"])
    if "eq" in pred:
        return str(fact).lower() == str(pred["eq"]).lower()
    if "value" in pred or "contains_any" in pred:
        # Keyword containment: any of the keywords appears inside the (list-of-strings / string) fact.
        values = pred.get("value") or pred.get("contains_any")
        hay = " ".join(str(x) for x in fact) if isinstance(fact, (list, tuple, set)) else str(fact)
        hay = hay.lower()
        return any(str(v).lower() in hay for v in values)
    return False


def _match_group(group: dict, ctx: dict) -> bool:
    checks = []
    if "all_of" in group:
        checks.append(all(_eval_node(p, ctx) for p in group["all_of"]))
    if "any_of" in group:
        checks.append(any(_eval_node(p, ctx) for p in group["any_of"]))
    return all(checks) if checks else False


def _eval_node(node: dict, ctx: dict) -> bool:
    """A node is either an atomic predicate (has 'fact') or a nested group."""
    if "fact" in node:
        return _match_predicate(node, ctx)
    return _match_group(node, ctx)


def evaluate_trigger(trigger: dict, ctx: dict) -> bool:
    try:
        return _eval_node(trigger, ctx)
    except (KeyError, TypeError, ValueError):
        # Malformed rule fails safe: it does not fire.
        return False


def evaluate_rules(rules: list[ClinicalRule], ctx: dict) -> list[ClinicalRule]:
    fired = []
    for rule in rules:
        if rule.enabled and rule.trigger and evaluate_trigger(rule.trigger, ctx):
            fired.append(rule)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    fired.sort(key=lambda r: priority_order.get(r.priority.value if hasattr(r.priority, "value") else r.priority, 3))
    return fired


# Facts that the preventive-care engine computes and rules may reference.
RULE_FACTS_DOC = {
    "age": "int | None — age in years from profile date_of_birth",
    "family_condition_keywords": "list[str] — family condition names (lowercase)",
    "flagged_test_keywords": "list[str] — abnormal test names from latest report",
    "latest_blood_pressure_systolic": "float | None",
    "latest_hba1c": "float | None",
    "bmi": "float | None",
}
