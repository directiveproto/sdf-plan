# Architecture

`sdf-plan` is a ToolGate-first safety library with optional PlanSpec support.

## Design Goals

1. Universal runtime gating
- Work across agent frameworks that emit tool calls.
2. Deterministic outcomes
- Same semantic input -> same decision path and idempotency behavior.
3. Backward compatibility
- Preserve PlanSpec flows while making ToolGate the primary path.
4. Thin integration surface
- Framework adapters should be lightweight wrappers over core API.
5. Production-safe defaults
- Unknown/risky operations should not silently pass.

## End-to-End Data Flow

### Propose flow

1. Input arrives (tool name + args, or normalized through adapters/parsers).
2. Input is normalized/canonicalized.
3. Tool is classified (category + risk flags).
4. Policy is resolved.
5. Lint checks run (tool-mode and context-sensitive checks).
6. Idempotency key is derived for write-like paths (if enabled).
7. Decision is emitted:
   - `ALLOW`
   - `REQUIRE_CONFIRM` (with resume token)
   - `WARN`
   - `BLOCK`

### Confirm flow

1. Token is verified (signature + expiry + binding claims).
2. User intent (`user_ok`) is applied.
3. Result is returned:
   - `ALLOW` with `confirmed=True`
   - or `BLOCK` with reason/error

## Core Components

### `sdf_plan.gate`

Responsibilities:
- Runtime decisioning (`propose`)
- Confirmation (`confirm`)
- Contracts and response models
- Token + idempotency orchestration

### `sdf_plan.policy`

Responsibilities:
- Tool classification and risk mapping
- Policy defaults and overrides
- Verification posture controls (`verify_before_write`, strict mode)

### `sdf_plan.lint`

Responsibilities:
- Tool-mode lint checks
- Plan-mode lint checks (for PlanSpec compatibility)

### `sdf_plan.core`

Responsibilities:
- Internal representation (IR) models
- Input normalization (OpenAI/generic/PlanSpec to common shape)
- Canonical hashing for deterministic keys/binding

### `sdf_plan.adapters`

Responsibilities:
- Framework translation only
- No policy duplication
- No independent decision logic

### `sdf_plan.integrations` (legacy)

Responsibilities:
- Compatibility for decomposition-client style usage
- Not the recommended path for ToolGate-first runtime gating

## Determinism and Consistency

Determinism relies on:
- canonical JSON hashing
- stable policy resolution order
- explicit decision/error vocabulary
- shared helper logic across gate/lint/policy internals

This avoids decision drift between integration paths.

## Security-Critical Boundaries

1. Secret management boundary
- Token signing secret comes from config; non-dev fallback is not production-safe.
2. Token trust boundary
- Confirm tokens bind scope/tool/args-hash and include expiry.
3. Replay boundary
- OSS is stateless by default; strict one-time replay protection is host-managed (via `jti` store).

## Extension Points

1. Custom tool risk map overrides
2. Host-level policy defaults
3. Custom `tool_args_validator` in strict mode
4. Custom adapters using `propose/confirm`
5. Host audit hooks (decision telemetry)

## What is intentionally out of scope

- Hosted identity and tenancy control
- Persistent replay stores
- Billing, quota, and enterprise governance layers

Those belong to hosted platforms (for example `sdf-cloud`), not this OSS library.
