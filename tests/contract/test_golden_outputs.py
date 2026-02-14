import json
from pathlib import Path

from sdf_plan.lint import lint_plan
from sdf_plan.policy import policy_annotate


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "minimal_policy_lint.json"


def test_golden_policy_and_lint_output():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    plan = payload["input_plan"]

    annotated, summary = policy_annotate(plan)
    findings = lint_plan(annotated, max_steps=12, safety_mode="safe")

    assert summary == payload["expected_summary"]
    assert findings == payload["expected_findings"]
