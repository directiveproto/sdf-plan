# API Reference

This document describes the stable public API for `sdf-plan` v0.2.x.

## Core ToolGate API

### `propose(tool_name, args=None, ctx=None, meta=None, run_context=None, policy=None)`

Runtime gate check for a proposed tool execution.

- Module: `sdf_plan.gate.tool_gate`
- Re-export: `from sdf_plan import propose`
- Returns: `ToolGateResponse`

Behavior summary:
- Classifies tool and risk.
- Runs tool-mode lint checks.
- Applies policy defaults/overrides.
- Derives idempotency key for write-like tools when enabled.
- Supports first-class `GateContext` (`workspace_id`, `user_id`, `session_id`, `metadata`).
- Returns one of: `ALLOW`, `REQUIRE_CONFIRM`, `WARN`, or `BLOCK`.

### `confirm(token, user_ok=True)`

Confirms a previously confirm-gated action.

- Module: `sdf_plan.gate.tool_gate`
- Re-export: `from sdf_plan import confirm`
- Returns: `ConfirmResponse`

Behavior summary:
- Verifies token signature and expiry.
- If valid and `user_ok=True`, returns `ALLOW` with `confirmed=True`.
- If invalid/expired/tampered, returns `BLOCK` with error code.

### `apropose(...)` and `aconfirm(...)`

Async wrappers over sync gate primitives.

- Module: `sdf_plan.gate.tool_gate`
- Re-export: `from sdf_plan import apropose, aconfirm`
- Behavior: equivalent semantics to `propose/confirm`

## Contract Models

Module: `sdf_plan.gate.contracts`

- `GateDecision`: `ALLOW | REQUIRE_CONFIRM | BLOCK | WARN`
- `GateErrorCode`: `INVALID_TOKEN | TOKEN_EXPIRED | TOKEN_TAMPERED | POLICY_BLOCKED`
- `ToolGateRequest`
- `ToolGateResponse`
- `ConfirmRequest`
- `ConfirmResponse`
- `GateContext`

Schema snapshots are frozen under:
- `tests/contract/snapshots/tool_gate_request.schema.json`
- `tests/contract/snapshots/tool_gate_response.schema.json`

## Policy API

Module: `sdf_plan.policy`

- `GatePolicy`
- `VerifyBeforeWriteMode`
- `load_tool_risk_map(..., version="v2")`
- `classify_tool(...)`
- `policy_annotate(...)` (PlanSpec mode)

Tool map versions:
- `v2` (default): expanded common tools/risk categories
- `v1`: compatibility alias map

## Configuration API

Module: `sdf_plan.config`

- `SdfPlanConfig`
- `configure(...)`

Key fields:
- `secret`
- `token_ttl`
- `audit_hook`
- `strict_args`
- `environment`

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

Thin adapters:
- `langgraph_tool_gate_node` (module: `sdf_plan.adapters.langgraph`)
- `crewai_tool_gate` (module: `sdf_plan.adapters.crewai`)
- `langchain_tool_gate` (module: `sdf_plan.adapters.langchain`)

BYO adapter guidance:
- `docs/ADAPTER_TEMPLATE.md`

