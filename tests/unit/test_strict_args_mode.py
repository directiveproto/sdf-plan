from __future__ import annotations

from sdf_plan import SdfPlanConfig, configure, propose
from sdf_plan.gate.contracts import GateDecision, GateErrorCode


def test_strict_args_rejects_unknown_meta_keys() -> None:
    configure(SdfPlanConfig(strict_args=True))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a"},
            ctx={"workspace_id": "ws-1"},
            meta={"workspace_id": "ws-1", "x_unknown": 1},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision == GateDecision.BLOCK
    assert out.error_code == GateErrorCode.POLICY_BLOCKED
    assert out.reason and "STRICT_ARGS_REJECTED" in out.reason


def test_strict_args_rejects_unknown_ctx_keys() -> None:
    configure(SdfPlanConfig(strict_args=True))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a"},
            ctx={"workspace_id": "ws-1", "team_id": "t-1"},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision == GateDecision.BLOCK
    assert out.error_code == GateErrorCode.POLICY_BLOCKED
    assert out.reason and "unknown ctx keys" in out.reason

