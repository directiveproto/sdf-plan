from sdf_plan.core import normalize_to_ir
from sdf_plan.inputs.planspec import parse_planspec
from sdf_plan.models import PlanSpecEnvelope


def test_planspec_dict_to_ir() -> None:
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Write report",
                "intent": "filesystem write report",
                "inputs": ["draft"],
                "outputs": ["report"],
                "depends_on": [],
                "stop_condition": "done",
                "fallback": "retry",
            },
            {
                "id": "S2",
                "type": "VERIFY",
                "title": "Check report",
                "intent": "verify report",
                "inputs": ["report"],
                "outputs": [],
                "depends_on": ["S1"],
                "stop_condition": "verified",
                "fallback": "fail",
            },
        ]
    }

    ir = normalize_to_ir(plan, input_format="planspec")
    assert ir.version == "sdf.ir.v1"
    assert len(ir.actions) == 2
    assert ir.actions[0].id == "S1"
    assert ir.actions[1].id == "S2"
    assert ir.actions[0].meta["step_type"] == "ACT"


def test_planspec_envelope_model_to_ir() -> None:
    env = PlanSpecEnvelope(
        plan_id="p1",
        template_key="default",
        confidence=0.9,
        steps=[
            {
                "id": "S1",
                "type": "ACT",
                "title": "Send mail",
                "intent": "send email",
                "inputs": [],
                "outputs": ["msg_id"],
                "depends_on": [],
                "stop_condition": "sent",
                "fallback": "abort",
            }
        ],
    )

    ir = normalize_to_ir(env.model_dump(), input_format="planspec")
    parsed = parse_planspec(env)
    assert len(ir.actions) == len(parsed) == 1
    assert ir.actions[0].tool_name == parsed[0]["tool_name"]
