from sdf_plan.models import PlanSpecEnvelope, PlanStep


def _sample_step() -> PlanStep:
    return PlanStep(
        id="S1",
        type="ACT",
        title="Send report",
        intent="send weekly report email",
        inputs=["ctx.report"],
        outputs=["ctx.sent"],
        depends_on=[],
        stop_condition="Email accepted by provider",
        fallback="queue_retry",
    )


def test_plan_minimal_construction_and_defaults():
    plan = PlanSpecEnvelope(
        plan_id="plan_123",
        template_key="default",
        confidence=0.9,
        steps=[_sample_step()],
    )
    assert plan.version == "sdf.v1.2"
    assert plan.mode_used == "deterministic"
    assert plan.lint == []
    assert plan.goal_spec == {}


def test_plan_deterministic_dump():
    p1 = PlanSpecEnvelope(
        plan_id="plan_123",
        template_key="default",
        confidence=0.9,
        steps=[_sample_step()],
    )
    p2 = PlanSpecEnvelope(
        plan_id="plan_123",
        template_key="default",
        confidence=0.9,
        steps=[_sample_step()],
    )
    assert p1.model_dump() == p2.model_dump()
