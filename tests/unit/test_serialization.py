from sdf_plan.models import PlanSpecEnvelope, PlanStep


def test_plan_round_trip_json():
    plan = PlanSpecEnvelope(
        plan_id="plan_rt",
        template_key="default",
        confidence=0.7,
        steps=[
            PlanStep(
                id="S1",
                type="ANALYZE",
                title="Analyze",
                intent="analyze",
                stop_condition="done",
                fallback="reduce_scope",
            )
        ],
    )
    raw = plan.model_dump_json()
    restored = PlanSpecEnvelope.model_validate_json(raw)
    assert restored.model_dump() == plan.model_dump()


def test_alias_schema_round_trip():
    step = PlanStep.model_validate(
        {
            "id": "S3",
            "type": "ACT",
            "title": "Transform",
            "intent": "transform data",
            "stop_condition": "done",
            "fallback": "reduce_scope",
            "io": {
                "inputs": [{"key": "ctx.in", "schema": {"type": "string"}}],
                "outputs": [{"key": "ctx.out", "schema": {"type": "string"}}],
            },
        }
    )
    dumped = step.model_dump(by_alias=True)
    assert dumped["io"]["inputs"][0]["schema"] == {"type": "string"}
