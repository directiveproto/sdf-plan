from sdf_plan.gate.contracts import GateDecision
from sdf_plan.policy import DEFAULT_GATE_POLICY, GatePolicy, VerifyBeforeWriteMode, default_policy


def test_gate_policy_defaults_are_safe() -> None:
    p = default_policy()
    assert p.unknown_tool == GateDecision.REQUIRE_CONFIRM
    assert p.write_requires_confirm is True
    assert p.require_idempotency_for_write is True
    assert p.verify_before_write == VerifyBeforeWriteMode.WARN
    assert p.strict_mode is False


def test_default_policy_returns_copy() -> None:
    p1 = default_policy()
    p2 = default_policy()
    assert p1 is not p2
    p1.strict_mode = True
    assert p2.strict_mode is False


def test_gate_policy_model_validate() -> None:
    p = GatePolicy.model_validate({"strict_mode": True, "unknown_tool": "BLOCK"})
    assert p.strict_mode is True
    assert p.unknown_tool == GateDecision.BLOCK


def test_default_gate_policy_constant() -> None:
    assert isinstance(DEFAULT_GATE_POLICY, GatePolicy)
