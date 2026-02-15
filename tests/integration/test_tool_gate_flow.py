from sdf_plan import confirm, propose
from sdf_plan.gate.contracts import GateDecision


def test_block_confirm_allow_flow() -> None:
    # write tool -> blocked until confirmation
    first = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "hello"},
        meta={"workspace_id": "ws-1"},
        run_context={"workspace_id": "ws-1"},
    )
    assert first.decision == GateDecision.BLOCK
    assert first.resume is not None
    assert first.resume.token
    assert first.resume.idempotency_key

    c = confirm(first.resume.token, user_ok=True)
    assert c.decision == GateDecision.ALLOW
    assert c.confirmed is True
    assert c.idempotency_key == first.resume.idempotency_key

    second = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "hello"},
        meta={"workspace_id": "ws-1", "confirmed_token": first.resume.token},
        run_context={"workspace_id": "ws-1"},
    )
    assert second.decision == GateDecision.ALLOW


def test_unknown_tool_default_path_blocks_with_confirm_prompt() -> None:
    out = propose("totally.unknown.tool", {"x": 1})
    assert out.decision == GateDecision.BLOCK
    assert out.reason in {"UNKNOWN_TOOL", "REQUIRES_CONFIRM"}
    assert out.resume is not None
    assert out.resume.token is not None


def test_strict_mode_unknown_tool_is_hard_block() -> None:
    out = propose("unknown.alpha", {"x": 1}, policy={"strict_mode": True})
    assert out.decision == GateDecision.BLOCK
    assert out.error_code is not None
    assert out.resume is None


def test_verify_before_write_run_context_warn_path() -> None:
    out = propose(
        "filesystem.write",
        {"path": "/tmp/x", "content": "x"},
        policy={"write_requires_confirm": False, "verify_before_write": "WARN"},
        run_context={"recent_actions": []},
    )
    assert out.decision == GateDecision.WARN
    assert out.reason == "NO_VERIFY_BEFORE_WRITE"


def test_verify_before_write_run_context_enforce_path() -> None:
    out = propose(
        "filesystem.write",
        {"path": "/tmp/x", "content": "x"},
        policy={"write_requires_confirm": False, "verify_before_write": "ENFORCE"},
        run_context={"recent_actions": []},
    )
    assert out.decision == GateDecision.BLOCK
    assert out.reason == "NO_VERIFY_BEFORE_WRITE"
