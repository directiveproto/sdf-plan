import json
from pathlib import Path

from sdf_plan.models import PlanSpecEnvelope
from sdf_plan.policy import policy_annotate


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "compat"


def _upgrade_legacy(payload: dict) -> dict:
    if "steps" in payload:
        steps = payload["steps"]
    else:
        steps = payload.get("nodes", [])
    for step in steps:
        step.setdefault("title", step.get("intent", "Untitled"))
        step.setdefault("inputs", [])
        step.setdefault("outputs", [])
        step.setdefault("depends_on", [])
        step.setdefault("stop_condition", "done")
        step.setdefault("fallback", "reduce_scope")
        step.setdefault("retry", 0)
        step.setdefault("time_budget_sec", 0)
    upgraded = {
        "plan_id": payload.get("plan_id", "compat_plan"),
        "version": "sdf.v1.2",
        "template_key": payload.get("template_key", "compat"),
        "confidence": payload.get("confidence", 0.5),
        "mode_used": "deterministic",
        "goal_spec": payload.get("goal_spec", {}),
        "steps": steps,
        "lint": [],
    }
    return upgraded


def test_compat_v0_and_v1_fixtures_upgrade():
    for name in ("v0.json", "v1.json"):
        raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        upgraded = _upgrade_legacy(raw)
        upgraded_plan, summary = policy_annotate({"steps": upgraded["steps"]})
        upgraded["steps"] = upgraded_plan["steps"]
        upgraded["policy_summary"] = summary
        validated = PlanSpecEnvelope.model_validate(upgraded)
        assert validated.version == "sdf.v1.2"
        assert len(validated.steps) >= 1
