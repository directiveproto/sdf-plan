import json
from pathlib import Path

from sdf_plan.lint import _has_cycle
from sdf_plan.policy import policy_annotate


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "large_plan.json"


def test_large_plan_invariants_hold():
    plan = json.loads(FIXTURE.read_text(encoding="utf-8"))
    annotated, _summary = policy_annotate(plan)
    steps = annotated["steps"]

    assert len(steps) >= 20
    assert _has_cycle(steps) is False

    step_ids = {s["id"] for s in steps}
    for step in steps:
        for dep in step.get("depends_on", []):
            assert dep in step_ids
