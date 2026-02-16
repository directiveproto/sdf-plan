# Production Hardening Guide

## 1. Secret management
- Set a strong secret via `SDF_PLAN_TOKEN_SECRET` or `configure(SdfPlanConfig(secret=...))`.
- Development fallback emits a `RuntimeWarning`; do not rely on it outside local development.
- Rotate secret on a schedule; rotate immediately if leakage is suspected.

## 2. Replay strategy
- Confirmation tokens are signed and time-bounded.
- Confirmation tokens include a `jti` claim. For strict replay prevention, store consumed `jti` values in your hosted layer and reject duplicates.
- Keep token TTL short for sensitive tools.

## 3. Context discipline
- Always pass `GateContext` with at least `workspace_id`.
- Include `user_id` and `session_id` for auditability.
- Do not depend on legacy context in `meta` or `run_context` long term.

## 4. Audit logging
- Configure `SdfPlanConfig(audit_hook=...)` to capture decisions centrally.
- Persist decision, reason, tool, risk flags, idempotency key, and workspace context.

## 5. Strict mode
- Enable `strict_args=True` to reject unknown top-level keys in `meta` and `ctx`.
- In strict mode, write tools require `ctx.workspace_id` (scope is mandatory).
- Optionally configure `tool_args_validator(tool_name, args)` for deep tool payload checks.
- Strict hashing rejects non-JSON-native values in strict mode paths.
- Use this when handling untrusted tool-call payloads.

### Strict mode rollout checklist

1. Set `SDF_PLAN_TOKEN_SECRET` and `environment="production"`.
2. Ensure every write path passes `ctx.workspace_id`.
3. Enable `strict_args=True` in staging first.
4. Add `tool_args_validator` for high-risk tools.
5. Add replay store keyed by token `jti`.

