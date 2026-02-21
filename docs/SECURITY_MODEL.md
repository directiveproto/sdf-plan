# Security Model

This document defines the security posture and boundaries for `sdf-plan`.

## Scope and Threat Model

`sdf-plan` is a runtime safety library. It is designed to:
1. Prevent unsafe tool execution from silently proceeding.
2. Bind confirmation to a specific intended action.
3. Improve retry safety with deterministic idempotency derivation.

It is not a complete security platform. Out of scope:
- identity provider and tenant authz systems
- key vault/KMS operations
- transport/network security
- persistent replay prevention store

## Confirmation Token Model

Confirmation tokens are:
1. Signed with HMAC.
2. Time-bounded (`exp` claim).
3. Bound to:
   - tool name
   - canonical args hash
   - optional scope/workspace context
4. Issued with `jti` for host replay tracking.

### Security guarantees

Token verification prevents:
- payload tampering (signature mismatch)
- stale confirmations (expired tokens)
- cross-action reuse (binding mismatch if tool/args differ)

### Stable token-related errors

- `INVALID_TOKEN`
- `TOKEN_TAMPERED`
- `TOKEN_EXPIRED`

Hosted environments may enforce additional stricter codes.

## Replay Protection

Important:
- OSS `confirm(...)` is stateless.
- Strict one-time semantics require host storage keyed by token identity (`jti`).

Recommended host algorithm:
1. Verify token and extract `jti`.
2. Check replay store (`workspace_id + jti`).
3. If unseen, execute `confirm(token, user_ok=True)`.
4. Mark `jti` as consumed atomically.

If your host needs hard one-time guarantees, this step is mandatory.

## Secret Management

Production requirement:
- set `SDF_PLAN_TOKEN_SECRET` (or configure secret explicitly via `SdfPlanConfig`).

Development fallback:
- available only for local/dev flow
- emits warning
- not suitable for deployed usage

Recommended secret handling:
1. 256-bit random secret minimum
2. managed secret store (for example cloud secret manager)
3. periodic rotation with overlapping accept window in host layer

## Scope and Context Requirements

Recommended baseline:
- always pass `GateContext(workspace_id=...)`.

Strict mode hardening:
- write-like actions should require workspace scope.
- missing scope should be blocked rather than downgraded.

This reduces cross-tenant mistakes and accidental global behavior.

## Deterministic Idempotency

For write paths, idempotency keys are derived from:
- scope/workspace
- tool name
- canonical args hash

Benefits:
- prevents duplicate side effects on retries
- provides consistent deduping key for host runtimes

## Strict Mode Hardening

When strict controls are enabled:
- invalid/unknown top-level payload fields are rejected
- non-JSON-native types can be rejected in hashing paths
- optional deep tool-args validator can enforce host schemas
- scope requirements are enforced for sensitive/write actions

## Adapter Security Posture

Adapters must be thin wrappers.

Do:
- translate framework payloads
- call `propose/confirm`
- propagate decisions/errors faithfully

Do not:
- fork policy logic
- bypass token validation semantics
- mutate caller args/context objects

## OSS vs Hosted Responsibility Split

OSS (`sdf-plan`) handles:
- deterministic local decisioning
- token cryptographic checks
- lint/policy orchestration

Hosted platform handles:
- identity, tenancy, and policy governance
- replay store persistence (`jti`)
- auditing, retention, billing, and quota controls

## Security Validation

Security-focused tests should cover:
1. token tamper rejection
2. token expiry enforcement
3. token binding mismatch handling
4. replay behavior and host replay strategy
5. strict-mode scope and payload validation paths
6. concurrency behavior on propose/confirm flows

See:
- `tests/unit/test_token_security.py`
- `tests/integration/test_tool_gate_concurrency.py`
- contract and integration suites in `tests/`
