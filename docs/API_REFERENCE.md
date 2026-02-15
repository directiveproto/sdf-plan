# API Reference

This document describes the stable public API for `sdf-plan` v0.2.x.

## Core ToolGate API

### `propose(tool_name, args=None, meta=None, policy=None, run_context=None)`

Runtime gate check for a proposed tool execution.

- Module: `sdf_plan.gate.tool_gate`
- Re-export: `from sdf_plan import propose`
- Returns: `ToolGateResponse`

Behavior summary:
- Classifies tool and risk.
- Runs tool-mode lint checks.
- Applies policy defaults/overrides.
- Derives idempotency key for write-like tools when enabled.
- Returns one of: `ALLOW`, `WARN`, or `BLOCK` (confirm-required currently returns `BLOCK` with `resume.token`).

### `confirm(token, user_ok=True)`

Confirms a previously blocked action.

- Module: `sdf_plan.gate.tool_gate`
- Re-export: `from sdf_plan import confirm`
- Returns: `ConfirmResponse`

Behavior summary:
- Verifies token signature and expiry.
- If valid and `user_ok=True`, returns `ALLOW` with `confirmed=True`.
- If invalid/expired/tampered, returns `BLOCK` with error code.

## Contract Models

Module: `sdf_plan.gate.contracts`

- `GateDecision`: `ALLOW | REQUIRE_CONFIRM | BLOCK | WARN`
- `GateErrorCode`: `INVALID_TOKEN | TOKEN_EXPIRED | TOKEN_TAMPERED | POLICY_BLOCKED`
- `ToolGateRequest`
- `ToolGateResponse`
- `ConfirmRequest`
- `ConfirmResponse`

Schema snapshots are frozen under:
- `tests/contract/snapshots/tool_gate_request.schema.json`
- `tests/contract/snapshots/tool_gate_response.schema.json`

## Policy API

Module: `sdf_plan.policy`

- `GatePolicy`
- `VerifyBeforeWriteMode`
- `load_tool_risk_map(...)`
- `classify_tool(...)`
- `policy_annotate(...)` (PlanSpec mode)

## IR and Normalization API

Module: `sdf_plan.core`

- `normalize_to_ir(...)`
- `toolcalls_to_ir(...)`
- `planspec_to_ir(...)`
- `ir_to_planspec(...)`
- `IRSequence`
- `IRAction`

## PlanSpec APIs (Backward Compatible)

- `lint_plan(...)`
- `preflight_lint(...)`
- `policy_annotate(...)`
- `PlanSpecEnvelope`
- `PlanStep`

## Adapter API

Official adapter in v0.2.0:
- `langgraph_tool_gate_node` (module: `sdf_plan.adapters.langgraph`)

BYO adapter guidance:
- `docs/ADAPTER_TEMPLATE.md`
