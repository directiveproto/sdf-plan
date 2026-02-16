from __future__ import annotations

import sdf_plan.gate.tool_gate as tg
from sdf_plan import confirm, propose
from sdf_plan.gate.contracts import GateDecision, GateErrorCode


def _write_token(*, workspace_id: str = "ws-1", args: dict | None = None) -> str:
    out = propose(
        "filesystem.write",
        args or {"path": "/tmp/a", "content": "hello"},
        meta={"workspace_id": workspace_id},
        run_context={"workspace_id": workspace_id},
    )
    assert out.resume is not None
    assert out.resume.token is not None
    return out.resume.token


def test_token_tamper_is_rejected() -> None:
    token = _write_token()
    payload, sig = token.split(".")
    tampered_sig = ("A" if sig[0] != "A" else "B") + sig[1:]
    tampered = f"{payload}.{tampered_sig}"

    out = confirm(tampered)
    assert out.decision == GateDecision.BLOCK
    assert out.confirmed is False
    assert out.error_code == GateErrorCode.TOKEN_TAMPERED


def test_token_expiry_is_enforced(monkeypatch) -> None:
    monkeypatch.setattr(tg, "_now", lambda: 1000)
    token = _write_token()

    monkeypatch.setattr(tg, "_now", lambda: 1000 + 601)
    out = confirm(token)
    assert out.decision == GateDecision.BLOCK
    assert out.confirmed is False
    assert out.error_code == GateErrorCode.TOKEN_EXPIRED


def test_confirmed_token_is_bound_to_tool_and_args_hash() -> None:
    token = _write_token(args={"path": "/tmp/a", "content": "hello"})

    # Same token but different args must not auto-allow continuation.
    out = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "DIFFERENT"},
        meta={"workspace_id": "ws-1", "confirmed_token": token},
        run_context={"workspace_id": "ws-1"},
    )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
    assert out.resume is not None
    assert out.resume.token is not None


def test_confirmed_token_workspace_mismatch_does_not_auto_allow() -> None:
    token = _write_token(workspace_id="ws-1")

    out = propose(
        "filesystem.write",
        {"path": "/tmp/a", "content": "hello"},
        meta={"workspace_id": "ws-2", "confirmed_token": token},
        run_context={"workspace_id": "ws-2"},
    )
    assert out.decision == GateDecision.REQUIRE_CONFIRM
    assert out.resume is not None
    assert out.resume.token is not None


def test_confirm_replay_behavior_is_explicit_stateless_allow() -> None:
    token = _write_token()

    c1 = confirm(token)
    c2 = confirm(token)

    assert c1.decision == GateDecision.ALLOW
    assert c1.confirmed is True
    assert c2.decision == GateDecision.ALLOW
    assert c2.confirmed is True
