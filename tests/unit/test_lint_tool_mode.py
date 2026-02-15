from sdf_plan.gate.contracts import GateDecision
from sdf_plan.lint import lint_tool_mode


def _codes(findings):
    return [f["code"] for f in findings]


def test_unknown_tool_default_emits_unknown_tool() -> None:
    findings = lint_tool_mode(tool_name="unknown.tool")
    assert "UNKNOWN_TOOL" in _codes(findings)


def test_unknown_tool_block_policy_emits_error() -> None:
    findings = lint_tool_mode(tool_name="unknown.tool", policy={"unknown_tool": GateDecision.BLOCK.value})
    by_code = {f["code"]: f["level"] for f in findings}
    assert by_code["UNKNOWN_TOOL"] == "ERROR"


def test_write_requires_confirm_rule() -> None:
    findings = lint_tool_mode(tool_name="filesystem.write", args={"path": "/a"}, meta={})
    assert "WRITE_REQUIRES_CONFIRM" in _codes(findings)


def test_act_without_idempotency_only_when_auto_disabled() -> None:
    findings = lint_tool_mode(
        tool_name="filesystem.write",
        args={"path": "/a"},
        meta={"disable_auto_idempotency": True},
    )
    assert "ACT_WITHOUT_IDEMPOTENCY" in _codes(findings)


def test_no_verify_before_write_context_gated() -> None:
    no_ctx = lint_tool_mode(
        tool_name="filesystem.write",
        policy={"write_requires_confirm": False, "verify_before_write": "WARN"},
        run_context=None,
    )
    assert "NO_VERIFY_BEFORE_WRITE" not in _codes(no_ctx)

    with_ctx = lint_tool_mode(
        tool_name="filesystem.write",
        policy={"write_requires_confirm": False, "verify_before_write": "WARN"},
        run_context={"recent_actions": []},
    )
    assert "NO_VERIFY_BEFORE_WRITE" in _codes(with_ctx)


def test_no_verify_before_write_enforce_is_error() -> None:
    findings = lint_tool_mode(
        tool_name="filesystem.write",
        policy={"write_requires_confirm": False, "verify_before_write": "ENFORCE"},
        run_context={"recent_actions": []},
    )
    for f in findings:
        if f["code"] == "NO_VERIFY_BEFORE_WRITE":
            assert f["level"] == "ERROR"
            break
    else:
        raise AssertionError("NO_VERIFY_BEFORE_WRITE not found")
