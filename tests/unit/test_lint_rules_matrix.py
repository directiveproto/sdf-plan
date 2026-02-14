from __future__ import annotations

from copy import deepcopy

import pytest

from sdf_plan.lint import LINT_RULES_EVALUATED, lint_plan


def _base_plan() -> dict:
    return {
        "steps": [
            {
                "id": "S1",
                "type": "ANALYZE",
                "title": "Analyze",
                "intent": "analyze data",
                "inputs": [],
                "outputs": ["ctx.analysis"],
                "depends_on": [],
                "stop_condition": "Analysis artifact generated",
                "fallback": "reduce_scope",
            },
            {
                "id": "S2",
                "type": "ACT",
                "title": "Send",
                "intent": "send invoice email",
                "inputs": ["ctx.analysis"],
                "outputs": ["ctx.sent"],
                "depends_on": ["S1"],
                "stop_condition": "Provider accepted request",
                "fallback": "queue_retry",
                "confirm": "Confirm before sending",
                "idempotency_key": "idem_s2",
            },
            {
                "id": "S3",
                "type": "VERIFY",
                "title": "Verify",
                "intent": "verify provider status",
                "inputs": ["ctx.sent"],
                "outputs": ["ctx.verified"],
                "depends_on": ["S2"],
                "stop_condition": "Provider status code is 200",
                "fallback": "manual_review",
            },
        ]
    }


def _codes(findings: list[dict]) -> set[str]:
    return {f["code"] for f in findings}


def test_baseline_has_no_lint_findings():
    findings = lint_plan(_base_plan(), max_steps=12, safety_mode="safe")
    assert findings == []


@pytest.mark.parametrize("rule_code", LINT_RULES_EVALUATED)
def test_each_rule_can_be_triggered(rule_code: str):
    plan = _base_plan()
    max_steps = 12

    if rule_code == "PLAN_TOO_LONG":
        max_steps = 2
    elif rule_code == "MISSING_STOP_CONDITION":
        plan["steps"][0]["stop_condition"] = ""
    elif rule_code == "MISSING_FALLBACK":
        plan["steps"][0]["fallback"] = ""
    elif rule_code == "UNVERIFIABLE_STOP":
        plan["steps"][0]["stop_condition"] = "Step S1 completed"
    elif rule_code == "CYCLE_DETECTED":
        plan["steps"][0]["depends_on"] = ["S3"]
    elif rule_code == "DUPLICATE_OUTPUT_KEY":
        plan["steps"][1]["outputs"] = ["ctx.analysis"]
    elif rule_code == "UNUSED_OUTPUT":
        plan["steps"][0]["outputs"].append("ctx.unused")
    elif rule_code == "ACT_WITHOUT_IDEMPOTENCY":
        plan["steps"][1].pop("idempotency_key", None)
    elif rule_code == "WRITE_WITHOUT_CONFIRM":
        plan["steps"][1].pop("confirm", None)
    elif rule_code == "NO_VERIFY_BEFORE_WRITE":
        plan["steps"] = deepcopy(plan["steps"][:2])
    else:
        raise AssertionError(f"Unhandled lint rule: {rule_code}")

    findings = lint_plan(plan, max_steps=max_steps, safety_mode="safe")
    assert rule_code in _codes(findings)
