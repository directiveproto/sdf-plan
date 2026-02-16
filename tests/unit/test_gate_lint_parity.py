from __future__ import annotations

from sdf_plan import propose
from sdf_plan.gate.contracts import GateDecision
from sdf_plan.lint import lint_tool_mode


def _codes(findings: list[dict]) -> set[str]:
    return {str(f.get("code")) for f in findings}


def test_verify_before_write_parity_between_lint_and_gate() -> None:
    no_verify_ctx = {"recent_actions": []}
    policy = {"write_requires_confirm": False, "verify_before_write": "ENFORCE"}

    lint_findings = lint_tool_mode(
        tool_name="filesystem.write",
        args={"path": "/tmp/a", "content": "x"},
        policy=policy,
        run_context=no_verify_ctx,
    )
    gate = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "x"},
        ctx={"workspace_id": "ws-1"},
        policy=policy,
        run_context=no_verify_ctx,
    )
    assert "NO_VERIFY_BEFORE_WRITE" in _codes(lint_findings)
    assert gate.decision == GateDecision.BLOCK
    assert gate.reason == "NO_VERIFY_BEFORE_WRITE"


def test_write_classification_parity_between_lint_and_gate() -> None:
    write_lints = lint_tool_mode(
        tool_name="filesystem.write",
        args={"path": "/tmp/a", "content": "x"},
        meta={},
    )
    read_lints = lint_tool_mode(
        tool_name="filesystem.read",
        args={"path": "/tmp/a"},
        meta={},
    )
    write_gate = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "x"},
        ctx={"workspace_id": "ws-1"},
    )
    read_gate = propose(
        "filesystem.read",
        {"path": "/tmp/a"},
        ctx={"workspace_id": "ws-1"},
    )

    assert "WRITE_REQUIRES_CONFIRM" in _codes(write_lints)
    assert "WRITE_REQUIRES_CONFIRM" not in _codes(read_lints)
    assert write_gate.decision == GateDecision.REQUIRE_CONFIRM
    assert read_gate.decision == GateDecision.ALLOW

