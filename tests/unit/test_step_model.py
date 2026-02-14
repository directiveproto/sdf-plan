from sdf_plan.models import PlanStep


def test_step_defaults():
    step = PlanStep(
        id="S1",
        type="ANALYZE",
        title="Analyze",
        intent="analyze inputs",
        stop_condition="Analysis complete",
        fallback="reduce_scope",
    )
    assert step.retry == 0
    assert step.time_budget_sec == 0
    assert step.confirm is None
    assert step.inputs == []
    assert step.outputs == []
    assert step.depends_on == []


def test_step_enriched_fields():
    step = PlanStep.model_validate(
        {
            "id": "S2",
            "type": "ACT",
            "title": "Write",
            "intent": "write output",
            "stop_condition": "Write acknowledged",
            "fallback": "abort",
            "idempotency_key": "idem_1",
            "stop": {"kind": "string", "hint": "Write acknowledged", "expr": None},
            "policy": {
                "requires_confirm": True,
                "confirm_prompt": "Confirm",
                "risk_flags": ["external_write"],
            },
            "io": {
                "inputs": [{"key": "ctx.input", "schema": {"type": "string"}}],
                "outputs": [{"key": "ctx.output", "schema": {"type": "string"}}],
            },
        }
    )
    assert step.idempotency_key == "idem_1"
    assert step.policy is not None and step.policy.requires_confirm is True
    assert step.io is not None and step.io.outputs[0].key == "ctx.output"
