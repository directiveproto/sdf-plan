from __future__ import annotations

import json
from pathlib import Path

from sdf_plan.gate.contracts import (
    ConfirmRequest,
    ConfirmResponse,
    GateDecision,
    GateErrorCode,
    ToolGateRequest,
    ToolGateResponse,
)

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _load_snapshot(name: str) -> dict:
    with (SNAPSHOT_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def test_gate_decision_enum_is_stable() -> None:
    assert [e.value for e in GateDecision] == [
        "ALLOW",
        "REQUIRE_CONFIRM",
        "BLOCK",
        "WARN",
    ]


def test_gate_error_codes_are_stable() -> None:
    assert [e.value for e in GateErrorCode] == [
        "INVALID_TOKEN",
        "TOKEN_EXPIRED",
        "TOKEN_TAMPERED",
        "POLICY_BLOCKED",
    ]


def test_tool_gate_request_schema_snapshot() -> None:
    actual = ToolGateRequest.model_json_schema()
    expected = _load_snapshot("tool_gate_request.schema.json")
    assert actual == expected


def test_tool_gate_response_schema_snapshot() -> None:
    actual = ToolGateResponse.model_json_schema()
    expected = _load_snapshot("tool_gate_response.schema.json")
    assert actual == expected


def test_confirm_contract_shapes_exist() -> None:
    # Ensure confirm contracts are importable and schema-generated as part of freeze.
    assert ConfirmRequest.model_json_schema()["type"] == "object"
    assert ConfirmResponse.model_json_schema()["type"] == "object"
