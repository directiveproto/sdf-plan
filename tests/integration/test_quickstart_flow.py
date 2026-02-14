import json

from sdf_plan.lint import _has_cycle, lint_plan
from sdf_plan.models import PlanSpecEnvelope
from sdf_plan.policy import policy_annotate


def test_quickstart_golden_path(tmp_path):
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "send email",
                "intent": "send email to customer",
                "inputs": [],
                "outputs": ["ctx.sent"],
                "depends_on": [],
                "stop_condition": "Email accepted by provider",
                "fallback": "reduce_scope",
                "retry": 0,
                "time_budget_sec": 120,
                "confirm": None,
                "idempotency_key": "idem_s1",
            },
            {
                "id": "S2",
                "type": "VERIFY",
                "title": "verify delivery",
                "intent": "verify provider acknowledged",
                "inputs": ["ctx.sent"],
                "outputs": ["ctx.verified"],
                "depends_on": ["S1"],
                "stop_condition": "Provider ACK recorded",
                "fallback": "manual_review",
                "retry": 0,
                "time_budget_sec": 120,
                "confirm": None,
            },
        ]
    }

    plan, summary = policy_annotate(plan)
    findings = lint_plan(plan, max_steps=12, safety_mode="safe")
    out = {
        "plan_id": "plan_quickstart",
        "version": "sdf.v1.2",
        "template_key": "default",
        "confidence": 0.9,
        "mode_used": "deterministic",
        "goal_spec": {"goal": "send status email"},
        "steps": plan["steps"],
        "lint": findings,
        "policy_summary": summary,
    }

    out_path = tmp_path / "plan.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    loaded = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert len(loaded["steps"]) == 2
    assert len({s["id"] for s in loaded["steps"]}) == len(loaded["steps"])
    assert _has_cycle(loaded["steps"]) is False

    # Schema-level validation for integration output envelope.
    PlanSpecEnvelope.model_validate(loaded)
