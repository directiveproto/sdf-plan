# Production Hardening Guide

## 1. Secret management
- Set a strong secret via `SDF_PLAN_TOKEN_SECRET` or `configure(SdfPlanConfig(secret=...))`.
- Avoid development fallback outside local environments.
- Rotate secret on a schedule; rotate immediately if leakage is suspected.

## 2. Replay strategy
- Confirmation tokens are signed and time-bounded.
- For strict replay prevention, store consumed token IDs in your hosted layer and reject duplicates.
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
- Use this when handling untrusted tool-call payloads.

