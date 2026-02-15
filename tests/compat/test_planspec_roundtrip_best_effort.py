from __future__ import annotations

import pytest

from sdf_plan import ir_to_planspec, planspec_to_ir
from sdf_plan.models import PlanSpecEnvelope


def _sample_plan() -> dict:
    return {
        "plan_id": "p1",
        "template_key": "default",
        "confidence": 0.91,
        "mode_used": "deterministic",
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Send Email",
                "intent": "send email",
                "inputs": ["recipient", "body"],
                "outputs": ["message_id"],
                "depends_on": [],
                "stop_condition": "message delivered",
                "fallback": "manual_review",
                "retry": 1,
                "time_budget_sec": 30,
                "confirm": "Confirm send",
                "idempotency_key": "idem_abc",
            }
        ],
    }


def test_planspec_to_ir_is_deterministic() -> None:
    plan = _sample_plan()
    ir1 = planspec_to_ir(plan).model_dump()
    ir2 = planspec_to_ir(plan).model_dump()
    assert ir1 == ir2


def test_ir_to_planspec_roundtrip_best_effort() -> None:
    original = PlanSpecEnvelope.model_validate(_sample_plan())
    ir = planspec_to_ir(original)
    restored = ir_to_planspec(
        ir,
        plan_id=original.plan_id,
        template_key=original.template_key,
        confidence=original.confidence,
        mode_used=original.mode_used,
    )

    assert restored.plan_id == original.plan_id
    assert restored.template_key == original.template_key
    assert len(restored.steps) == len(original.steps)
    assert restored.steps[0].id == original.steps[0].id
    assert restored.steps[0].type == original.steps[0].type
    assert restored.steps[0].inputs == original.steps[0].inputs
    assert restored.steps[0].outputs == original.steps[0].outputs
    assert restored.steps[0].depends_on == original.steps[0].depends_on


def test_ir_to_planspec_warns_on_non_lossless_fields() -> None:
    ir = planspec_to_ir(_sample_plan())
    ir.actions[0].args["raw_payload"] = {"x": 1}
    ir.actions[0].meta["framework_only"] = {"debug": True}

    with pytest.warns(UserWarning, match="Non-lossless mapping"):
        restored = ir_to_planspec(ir)

    assert restored.steps[0].id == "S1"
