import pytest
from pydantic import ValidationError

from sdf_plan.models import PlanSpecEnvelope, PlanStep


def test_invalid_plan_missing_required_fields():
    with pytest.raises(ValidationError, match="template_key"):
        PlanSpecEnvelope.model_validate({"plan_id": "x", "confidence": 0.5})


def test_invalid_step_wrong_type_raises_validation_error():
    with pytest.raises(ValidationError, match="retry"):
        PlanStep.model_validate(
            {
                "id": "S1",
                "type": "ANALYZE",
                "title": "Analyze",
                "intent": "analyze",
                "stop_condition": "done",
                "fallback": "reduce_scope",
                "retry": {"not": "an_int"},
            }
        )


def test_invalid_enum_value_raises():
    with pytest.raises(ValidationError, match="kind"):
        PlanStep.model_validate(
            {
                "id": "S1",
                "type": "ANALYZE",
                "title": "Analyze",
                "intent": "analyze",
                "stop_condition": "done",
                "fallback": "reduce_scope",
                "stop": {"kind": "invalid", "hint": "x", "expr": None},
            }
        )


def test_empty_steps_list_allowed():
    plan = PlanSpecEnvelope(
        plan_id="empty",
        template_key="default",
        confidence=0.1,
        steps=[],
    )
    assert plan.steps == []
