# Security Model

This document describes the security posture and guarantees for `sdf-plan` v0.2.x.

## Threat Model (Library Scope)

`sdf-plan` is an application library, not a full identity platform. It focuses on:

1. Preventing unsafe tool execution from silently proceeding.
2. Binding human confirmation to specific tool calls.
3. Reducing duplicate side effects via idempotency keys.

Out of scope:
- Key management infrastructure (KMS/HSM).
- Multi-tenant auth/authz backend.
- Network transport security (handled by host application).

## Confirmation Token Security

Tokens produced during confirm-required flows are:

1. Signed (HMAC) to prevent tampering.
2. Time-bounded (expiry enforced).
3. Issued with a unique token ID (`jti`) for replay tracking in hosted layers.
3. Bound to:
- tool name
- canonical args hash
- optional scope/workspace context

Validation errors map to stable codes:
- `INVALID_TOKEN`
- `TOKEN_TAMPERED`
- `TOKEN_EXPIRED`

### Replay protection using `jti`

`sdf-plan` OSS token checks are stateless by design. For one-time confirmation semantics, hosts should store consumed token IDs.

Minimal pattern:

1. `verify_token(token)` to read `jti`.
2. Check `jti` against your replay store.
3. If unused, run `confirm(token, user_ok=True)`.
4. Mark `jti` as consumed atomically.

Recommended replay-store key:
- `workspace_id + jti`

## Idempotency and Determinism

Write-like actions can derive an idempotency key from:
- scope
- tool name
- canonicalized args hash

This helps host runtimes avoid duplicate side effects on retries.

## Policy Defaults

Default policy is safety-biased:
- unknown tools require gating action
- write-like tools require confirmation by default
- write idempotency is required by default

Policy is configurable to fit host risk tolerance.

## Adapter Safety

Official adapter in v0.2.0:
- LangGraph only.

Adapters are intentionally thin and should not reimplement policy logic.

## OSS vs Hosted Responsibilities

OSS library responsibilities:
- deterministic local decisioning
- token checks
- lint and policy flow

Hosted/cloud responsibilities (outside this repo):
- identity and workspace authorization
- persistence and replay protection stores (recommended key: token `jti`)
- audit log retention controls
- billing/rate-limit enforcement

## Validation and Tests

Security behavior is enforced by tests covering:
- token tamper rejection
- token expiry handling
- scope/tool/args binding behavior
- confirm replay semantics
- concurrency safety checks for propose/confirm
