from __future__ import annotations

from sdf_plan import SdfPlanConfig, configure, confirm, propose


def test_propose_invokes_audit_hook() -> None:
    events: list[dict] = []
    configure(SdfPlanConfig(audit_hook=events.append))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1", "metadata": {"source": "test"}},
        )
    finally:
        configure(SdfPlanConfig())

    assert out.resume is not None
    assert len(events) >= 1
    evt = events[-1]
    assert evt["event"] == "propose"
    assert evt["decision"] == out.decision.value
    assert evt["tool"] == "filesystem.write"
    assert "ctx" in evt


def test_confirm_invokes_audit_hook() -> None:
    events: list[dict] = []
    configure(SdfPlanConfig(audit_hook=events.append))
    try:
        first = propose(
            "filesystem.write",
            {"path": "/tmp/a", "content": "x"},
            ctx={"workspace_id": "ws-1"},
        )
        token = first.resume.token if first.resume else None
        assert token
        out = confirm(token)
    finally:
        configure(SdfPlanConfig())

    assert out.confirmed is True
    confirm_events = [e for e in events if e.get("event") == "confirm"]
    assert confirm_events
    assert confirm_events[-1]["decision"] == "ALLOW"

