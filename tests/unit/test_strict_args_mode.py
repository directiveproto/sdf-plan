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


def test_strict_mode_requires_workspace_scope_for_write_tools() -> None:
    configure(SdfPlanConfig(strict_args=True))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a"},
            ctx={},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision == GateDecision.BLOCK
    assert out.error_code == GateErrorCode.POLICY_BLOCKED
    assert out.reason and "STRICT_SCOPE_REQUIRED" in out.reason


def test_strict_mode_allows_read_without_workspace_scope() -> None:
    configure(SdfPlanConfig(strict_args=True))
    try:
        out = propose(
            "filesystem.read",
            {"path": "/tmp/a"},
            ctx={},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision in {GateDecision.ALLOW, GateDecision.WARN}


def test_strict_validator_success_path() -> None:
    def _validator(tool_name: str, args: dict[str, object]) -> None:
        assert tool_name == "filesystem.write"
        if "path" not in args:
            raise ValueError("missing path")

    configure(SdfPlanConfig(strict_args=True, tool_args_validator=_validator))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a"},
            ctx={"workspace_id": "ws-1"},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision == GateDecision.REQUIRE_CONFIRM


def test_strict_validator_reject_path() -> None:
    def _validator(_tool_name: str, _args: dict[str, object]) -> None:
        raise ValueError("bad args payload")

    configure(SdfPlanConfig(strict_args=True, tool_args_validator=_validator))
    try:
        out = propose(
            "filesystem.write",
            {"path": "/tmp/a"},
            ctx={"workspace_id": "ws-1"},
        )
    finally:
        configure(SdfPlanConfig())
    assert out.decision == GateDecision.BLOCK
    assert out.error_code == GateErrorCode.POLICY_BLOCKED
    assert out.reason and "STRICT_ARGS_VALIDATION_FAILED" in out.reason

