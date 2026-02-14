from sdf_plan.lint import (
    _has_cycle,
    _looks_like_external_write,
    _unverifiable_stop_condition,
    lint_plan,
)


def test_has_cycle_true_and_false():
    acyclic = [
        {"id": "S1", "depends_on": []},
        {"id": "S2", "depends_on": ["S1"]},
    ]
    cyclic = [
        {"id": "S1", "depends_on": ["S2"]},
        {"id": "S2", "depends_on": ["S1"]},
    ]
    assert _has_cycle(acyclic) is False
    assert _has_cycle(cyclic) is True


def test_write_keyword_detection():
    assert _looks_like_external_write("send invoice email") is True
    assert _looks_like_external_write("analyze records") is False


def test_unverifiable_stop_detection():
    assert _unverifiable_stop_condition("Step S1 completed") is True
    assert _unverifiable_stop_condition("HTTP status is 200") is False


def test_lint_is_deterministic():
    plan = {
        "steps": [
            {
                "id": "S1",
                "type": "ACT",
                "title": "Send",
                "intent": "send email",
                "inputs": [],
                "outputs": ["ctx.sent"],
                "depends_on": [],
                "stop_condition": "Step S1 completed",
                "fallback": "reduce_scope",
            }
        ]
    }
    a = lint_plan(plan, max_steps=12, safety_mode="safe")
    b = lint_plan(plan, max_steps=12, safety_mode="safe")
    assert a == b
