# API Reference

This document defines the stable public API for `sdf-plan` v0.2.x.

## Public Surface (Stable)

Primary imports:

```python
from sdf_plan import (
    propose,
    confirm,
    apropose,
    aconfirm,
    configure,
    SdfPlanConfig,
    GateContext,
)
```

Compatibility note:
- Top-level facade (`sdf_plan.__init__`) is stable.
- Internal modules may move, but behavior and contracts remain compatible within minor versions.

## Decisions and Errors

Decision vocabulary:
- `ALLOW`
- `REQUIRE_CONFIRM`
- `WARN`
- `BLOCK`

Core error codes:
- `INVALID_TOKEN`
- `TOKEN_EXPIRED`
- `TOKEN_TAMPERED`
- `POLICY_BLOCKED`

Cloud extensions may add stricter codes (for example replay/scope codes).

## ToolGate API

### `propose(...)`

```python
propose(
    tool_name: str,
    args: dict | None = None,
    ctx: GateContext | None = None,
    meta: dict | None = None,
    run_context: dict | None = None,
    policy: dict | GatePolicy | None = None,
) -> ToolGateResponse
```

Purpose:
- Evaluate a proposed tool execution before runtime side effects occur.

Recommended usage:
- Always pass `ctx=GateContext(...)`, especially `workspace_id`.
- Use `meta` for control data (`confirm_prompt`, `confirmed_token`).
- Use `run_context` for execution evidence/context (`verified_resources`, `session_id`).

Response fields:
- `decision`
- `reason`
- `error_code`
- `risk_flags`
- `confirm_prompt`
- `resume.token`
- `resume.idempotency_key`

### `confirm(...)`

```python
confirm(token: str, user_ok: bool = True) -> ConfirmResponse
```

Purpose:
- Validate and acknowledge a confirmation token.

Behavior:
- `user_ok=False` returns blocked/denied flow.
- Valid token + `user_ok=True` returns `ALLOW` with `confirmed=True`.
- Invalid/expired/tampered token returns `BLOCK` with error code.

### Async wrappers

```python
await apropose(...)
await aconfirm(...)
```

Semantics are equivalent to sync APIs.

## Context Contract

### `GateContext`

```python
GateContext(
    workspace_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
)
```

Notes:
- `workspace_id` is strongly recommended in all production usage.
- In strict mode, write paths may require workspace scope.

## Configuration API

### `SdfPlanConfig`

```python
SdfPlanConfig(
    secret: str | None = None,
    token_ttl: int = 600,
    audit_hook: Callable | None = None,
    strict_args: bool = False,
    environment: str = "development",
    tool_args_validator: Callable[[str, dict], None] | None = None,
)
```

### `configure(config)`

```python
configure(SdfPlanConfig(...)) -> None
```

Config semantics:
- Non-development environments require a real secret.
- Development fallback secret emits warning and is not for deployed usage.
- `strict_args=True` enables stricter payload validation.
- `tool_args_validator` allows host-defined deep schema enforcement.

## Policy API

Module: `sdf_plan.policy`

Key types/functions:
- `GatePolicy`
- `VerifyBeforeWriteMode`
- `load_tool_risk_map(..., version="v2")`
- `classify_tool(...)`
- `policy_annotate(...)` (PlanSpec mode)

Important knobs:
- `unknown_tool`
- `write_requires_confirm`
- `require_idempotency_for_write`
- `verify_before_write`
- `strict_mode`

Policy precedence (typical):
1. Explicit request-level policy
2. Host/runtime defaults
3. Library defaults

## Normalization and IR API

Module: `sdf_plan.core`

- `normalize_to_ir(...)`
- `toolcalls_to_ir(...)`
- `planspec_to_ir(...)`
- `ir_to_planspec(...)`
- `IRSequence`
- `IRAction`

Input modes supported:
- OpenAI-style tool-call payloads
- Generic tool-call JSON
- PlanSpec

## PlanSpec Compatibility API

Kept for backward compatibility:
- `lint_plan(...)`
- `preflight_lint(...)`
- `policy_annotate(...)`
- `PlanSpecEnvelope`
- `PlanStep`

Roundtrip caveat:
- PlanSpec <-> IR is deterministic best-effort, not guaranteed lossless.

## Adapter API

Thin adapters:
- `sdf_plan.adapters.langgraph.langgraph_tool_gate_node`
- `sdf_plan.adapters.crewai.crewai_tool_gate`
- `sdf_plan.adapters.langchain.langchain_tool_gate`

Custom adapters:
- Follow `docs/ADAPTER_TEMPLATE.md`.
- Keep adapter logic thin: convert framework payloads and call `propose/confirm`.

## Legacy Integrations

Legacy modules remain for compatibility:
- `sdf_plan.integrations.langgraph.sdf_node`
- `sdf_plan.integrations.crewai.SDFTool`

They are decomposition-client oriented, not ToolGate-first runtime gating.

## Schema Freeze / Contract Tests

Contract snapshots:
- `tests/contract/snapshots/tool_gate_request.schema.json`
- `tests/contract/snapshots/tool_gate_response.schema.json`

Related tests:
- `tests/contract/test_gate_contract.py`

Any schema change should be deliberate and documented in changelog/release notes.
