from __future__ import annotations

import asyncio
import warnings
from typing import Any

from sdf_plan._internal.policy_helpers import has_verify_context, is_write_tool
from sdf_plan._internal.token import issue_resume_token, now_epoch_seconds, verify_token
from sdf_plan.config import get_config
from sdf_plan.core.hashing import hash_canonical
from sdf_plan.gate.contracts import (
    ConfirmResponse,
    GateContext,
    GateDecision,
    GateErrorCode,
    ToolGateResponse,
)
from sdf_plan.gate.idempotency import generate_idempotency_key
from sdf_plan.lint import lint_tool_mode
from sdf_plan.policy import GatePolicy, VerifyBeforeWriteMode, classify_tool, load_tool_risk_map


def _now() -> int:
    # Backward-compatible shim for tests monkeypatching sdf_plan.gate.tool_gate._now.
    return now_epoch_seconds()


def _to_policy(policy: dict[str, Any] | GatePolicy | None) -> GatePolicy:
    if policy is None:
        return GatePolicy()
    if isinstance(policy, GatePolicy):
        return policy
    return GatePolicy.model_validate(policy)


def _context_from_legacy(meta: dict[str, Any], run_context: dict[str, Any]) -> GateContext:
    return GateContext(
        workspace_id=(
            run_context.get("workspace_id")
            or meta.get("workspace_id")
            or meta.get("tenant_id")
        ),
        user_id=run_context.get("user_id") or meta.get("user_id"),
        session_id=run_context.get("session_id") or meta.get("session_id"),
        metadata={},
    )


def _resolve_ctx(
    ctx: GateContext | dict[str, Any] | None,
    *,
    meta: dict[str, Any],
    run_context: dict[str, Any],
) -> GateContext:
    if ctx is not None:
        if isinstance(ctx, GateContext):
            return ctx
        return GateContext.model_validate(ctx)

    if meta or run_context:
        warnings.warn(
            "Passing workspace/user context via `meta` or `run_context` is deprecated. "
            "Use `ctx=GateContext(...)`.",
            DeprecationWarning,
            stacklevel=2,
        )
    return _context_from_legacy(meta, run_context)


def _run_context_with_ctx(run_context: dict[str, Any], ctx: GateContext) -> dict[str, Any]:
    merged = dict(run_context)
    if ctx.workspace_id and "workspace_id" not in merged:
        merged["workspace_id"] = ctx.workspace_id
    if ctx.user_id and "user_id" not in merged:
        merged["user_id"] = ctx.user_id
    if ctx.session_id and "session_id" not in merged:
        merged["session_id"] = ctx.session_id
    if ctx.metadata:
        extra = dict(merged.get("metadata") or {})
        extra.update(ctx.metadata)
        merged["metadata"] = extra
    return merged


def _emit_audit(payload: dict[str, Any]) -> None:
    hook = get_config().audit_hook
    if hook is None:
        return
    try:
        hook(payload)
    except Exception:
        # Audit must never break gate execution paths.
        return


def _strict_error(message: str) -> ToolGateResponse:
    return ToolGateResponse(
        decision=GateDecision.BLOCK,
        reason=message,
        error_code=GateErrorCode.POLICY_BLOCKED,
        risk_flags=[],
        confirm_prompt=None,
        resume=None,
    )


def _validate_strict_inputs(
    *,
    args: dict[str, Any],
    meta: dict[str, Any],
    ctx: GateContext,
    raw_ctx: GateContext | dict[str, Any] | None,
) -> str | None:
    allowed_meta = {
        "confirmed_token",
        "confirm_prompt",
        "idempotency_exclude_fields",
        "idempotency_key",
        "disable_auto_idempotency",
        "workspace_id",
        "tenant_id",
        "user_id",
        "session_id",
    }
    unknown_meta = sorted(k for k in meta.keys() if k not in allowed_meta)
    if unknown_meta:
        return f"STRICT_ARGS_REJECTED: unknown meta keys: {', '.join(unknown_meta)}"

    if isinstance(raw_ctx, dict):
        allowed_ctx = {"workspace_id", "user_id", "session_id", "metadata"}
        unknown_ctx_keys = sorted(k for k in raw_ctx.keys() if k not in allowed_ctx)
        if unknown_ctx_keys:
            return f"STRICT_ARGS_REJECTED: unknown ctx keys: {', '.join(unknown_ctx_keys)}"

    if not isinstance(ctx.metadata, dict):
        return "STRICT_ARGS_REJECTED: ctx.metadata must be an object"
    unknown_ctx = []
    for key in ctx.metadata.keys():
        if not isinstance(key, str):
            unknown_ctx.append(str(key))
    if unknown_ctx:
        return f"STRICT_ARGS_REJECTED: ctx.metadata keys must be strings: {', '.join(unknown_ctx)}"

    bad_arg_keys = [str(k) for k in args.keys() if not isinstance(k, str)]
    if bad_arg_keys:
        return f"STRICT_ARGS_REJECTED: non-string top-level arg keys: {', '.join(bad_arg_keys)}"

    return None


def confirm(token: str, user_ok: bool = True) -> ConfirmResponse:
    if not user_ok:
        out = ConfirmResponse(
            decision=GateDecision.BLOCK,
            confirmed=False,
            error_code=GateErrorCode.POLICY_BLOCKED,
            reason="User denied confirmation",
        )
        _emit_audit(
            {
                "event": "confirm",
                "decision": out.decision.value,
                "reason": out.reason,
                "confirmed": out.confirmed,
                "error_code": out.error_code.value if out.error_code else None,
            }
        )
        return out

    try:
        payload = verify_token(token, now_fn=_now)
    except ValueError as exc:
        code = str(exc)
        if code == "TOKEN_EXPIRED":
            err = GateErrorCode.TOKEN_EXPIRED
        elif code == "TOKEN_TAMPERED":
            err = GateErrorCode.TOKEN_TAMPERED
        else:
            err = GateErrorCode.INVALID_TOKEN
        out = ConfirmResponse(
            decision=GateDecision.BLOCK,
            confirmed=False,
            error_code=err,
            reason=code,
        )
        _emit_audit(
            {
                "event": "confirm",
                "decision": out.decision.value,
                "reason": out.reason,
                "confirmed": out.confirmed,
                "error_code": out.error_code.value if out.error_code else None,
            }
        )
        return out

    token_jti = payload.get("jti")
    out = ConfirmResponse(
        decision=GateDecision.ALLOW,
        confirmed=True,
        reason="CONFIRMED",
        idempotency_key=payload.get("idempotency_key"),
    )
    _emit_audit(
        {
            "event": "confirm",
            "decision": out.decision.value,
            "reason": out.reason,
            "confirmed": out.confirmed,
            "error_code": out.error_code.value if out.error_code else None,
            "idempotency_key": out.idempotency_key,
            "jti": token_jti,
            "legacy_token": token_jti is None,
        }
    )
    return out


def propose(
    tool_name: str,
    args: dict[str, Any] | None = None,
    ctx: GateContext | dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    run_context: dict[str, Any] | None = None,
    policy: dict[str, Any] | GatePolicy | None = None,
) -> ToolGateResponse:
    if (
        isinstance(ctx, dict)
        and bool(ctx)
        and meta is None
        and run_context is None
        and not any(k in ctx for k in {"workspace_id", "user_id", "session_id", "metadata"})
    ):
        warnings.warn(
            "Passing `meta` as the third positional argument is deprecated. "
            "Use propose(..., meta=...) or propose(..., ctx=GateContext(...)).",
            DeprecationWarning,
            stacklevel=2,
        )
        meta = dict(ctx)
        ctx = None

    tool_name_norm = (tool_name or "").strip().lower()
    args_norm = dict(args or {})
    meta_norm = dict(meta or {})
    run_ctx = dict(run_context or {})
    resolved_ctx = _resolve_ctx(ctx, meta=meta_norm, run_context=run_ctx)
    run_ctx = _run_context_with_ctx(run_ctx, resolved_ctx)

    gp = _to_policy(policy)
    cfg = get_config()
    strict_enabled = gp.strict_mode or bool(cfg.strict_args)
    if strict_enabled:
        strict_error = _validate_strict_inputs(
            args=args_norm,
            meta=meta_norm,
            ctx=resolved_ctx,
            raw_ctx=ctx,
        )
        if strict_error is not None:
            out = _strict_error(strict_error)
            _emit_audit(
                {
                    "event": "propose",
                    "tool": tool_name_norm,
                    "decision": out.decision.value,
                    "reason": out.reason,
                    "risk_flags": [],
                    "idempotency_key": None,
                    "ctx": resolved_ctx.model_dump(),
                    "meta": meta_norm,
                }
            )
            return out

    # 1) normalize / classify
    risk_map_overrides = None
    if isinstance(policy, dict):
        risk_map_overrides = policy.get("tool_risk_map_overrides")
    risk_map = load_tool_risk_map(risk_map_overrides)
    classification = classify_tool(tool_name_norm, risk_map)
    risk_flags = list(classification.risk_flags)
    is_write = is_write_tool(classification.category, risk_flags)
    is_unknown = classification.category == "unknown"

    # 2) lint checks
    lint_reason = None
    lint_findings = lint_tool_mode(
        tool_name=tool_name_norm,
        args=args_norm,
        meta=meta_norm,
        policy=gp,
        run_context=run_ctx if run_ctx else None,
    )
    if lint_findings:
        lint_reason = str(lint_findings[0].get("code") or "")

    verify_warning = False
    verify_block = False
    confirmed_token_legacy = False
    if is_write and gp.verify_before_write != VerifyBeforeWriteMode.OFF:
        if not has_verify_context(run_ctx):
            if gp.verify_before_write == VerifyBeforeWriteMode.WARN:
                verify_warning = True
            elif gp.verify_before_write == VerifyBeforeWriteMode.ENFORCE:
                verify_block = True

    # 3) policy checks
    policy_block = False
    requires_confirm = False

    if is_unknown:
        if gp.strict_mode:
            policy_block = True
        elif gp.unknown_tool == GateDecision.BLOCK:
            policy_block = True
        elif gp.unknown_tool == GateDecision.REQUIRE_CONFIRM:
            requires_confirm = True

    if is_write and gp.write_requires_confirm:
        requires_confirm = True

    if verify_block:
        policy_block = True

    # check whether a confirmed token has already satisfied confirmation
    confirmed_token = meta_norm.get("confirmed_token")
    if confirmed_token:
        args_h = hash_canonical(args_norm, strict=strict_enabled)
        expected_scope = resolved_ctx.workspace_id
        try:
            payload = verify_token(str(confirmed_token), now_fn=_now)
        except ValueError:
            payload = None
        if (
            payload
            and payload.get("tool") == tool_name_norm
            and payload.get("args_hash") == args_h
            and payload.get("scope") == expected_scope
        ):
            requires_confirm = False
            policy_block = False
            verify_warning = False
            verify_block = False
            confirmed_token_legacy = payload.get("jti") is None

    # 4) idempotency checks
    idempotency_key = None
    if is_write and gp.require_idempotency_for_write:
        if strict_enabled and not resolved_ctx.workspace_id:
            out = _strict_error("STRICT_SCOPE_REQUIRED: workspace_id is required for write tools in strict mode")
            _emit_audit(
                {
                    "event": "propose",
                    "tool": tool_name_norm,
                    "decision": out.decision.value,
                    "reason": out.reason,
                    "risk_flags": list(risk_flags),
                    "idempotency_key": None,
                    "ctx": resolved_ctx.model_dump(),
                    "meta": meta_norm,
                    "confirmed_token_legacy": confirmed_token_legacy,
                }
            )
            return out
        if cfg.tool_args_validator is not None:
            try:
                cfg.tool_args_validator(tool_name_norm, args_norm)
            except Exception as exc:
                out = _strict_error(f"STRICT_ARGS_VALIDATION_FAILED: {exc}")
                _emit_audit(
                    {
                        "event": "propose",
                        "tool": tool_name_norm,
                        "decision": out.decision.value,
                        "reason": out.reason,
                        "risk_flags": [],
                        "idempotency_key": None,
                        "ctx": resolved_ctx.model_dump(),
                        "meta": meta_norm,
                    }
                )
                return out
        scope = resolved_ctx.workspace_id or "global"
        exclude_fields = meta_norm.get("idempotency_exclude_fields") or []
        idempotency_key = generate_idempotency_key(
            scope=scope,
            tool_name=tool_name_norm,
            args=args_norm,
            exclude_fields=exclude_fields,
            strict=strict_enabled,
        )

    # 5) decision build
    lint_codes = {str(f.get("code")) for f in lint_findings}
    if "UNKNOWN_TOOL" in lint_codes and gp.strict_mode:
        policy_block = True

    if "ACT_WITHOUT_IDEMPOTENCY" in lint_codes:
        policy_block = True

    if policy_block:
        reason = "POLICY_BLOCKED"
        if verify_block:
            reason = "NO_VERIFY_BEFORE_WRITE"
        elif is_unknown:
            reason = "UNKNOWN_TOOL"
        out = ToolGateResponse(
            decision=GateDecision.BLOCK,
            reason=reason,
            error_code=GateErrorCode.POLICY_BLOCKED,
            risk_flags=risk_flags,
            confirm_prompt=None,
            resume=None,
        )
        _emit_audit(
            {
                "event": "propose",
                "tool": tool_name_norm,
                "decision": out.decision.value,
                "reason": out.reason,
                "risk_flags": list(risk_flags),
                "idempotency_key": None,
                "ctx": resolved_ctx.model_dump(),
                "meta": meta_norm,
                "confirmed_token_legacy": confirmed_token_legacy,
            }
        )
        return out

    if requires_confirm:
        args_h = hash_canonical(args_norm, strict=strict_enabled)
        token = issue_resume_token(
            tool_name=tool_name_norm,
            args_hash=args_h,
            scope=resolved_ctx.workspace_id,
            idempotency_key=idempotency_key,
            now_fn=_now,
        )
        prompt = meta_norm.get("confirm_prompt") or "Confirm before executing side-effecting action"
        out = ToolGateResponse(
            decision=GateDecision.REQUIRE_CONFIRM,
            reason="WRITE_REQUIRES_CONFIRM" if is_write else (lint_reason or "REQUIRES_CONFIRM"),
            risk_flags=risk_flags,
            confirm_prompt=str(prompt),
            resume={"token": token, "idempotency_key": idempotency_key},
        )
        _emit_audit(
            {
                "event": "propose",
                "tool": tool_name_norm,
                "decision": out.decision.value,
                "reason": out.reason,
                "risk_flags": list(risk_flags),
                "idempotency_key": idempotency_key,
                "ctx": resolved_ctx.model_dump(),
                "meta": meta_norm,
                "confirmed_token_legacy": confirmed_token_legacy,
            }
        )
        return out

    if verify_warning:
        out = ToolGateResponse(
            decision=GateDecision.WARN,
            reason="NO_VERIFY_BEFORE_WRITE",
            risk_flags=risk_flags,
            confirm_prompt=None,
            resume={"token": None, "idempotency_key": idempotency_key},
        )
        _emit_audit(
            {
                "event": "propose",
                "tool": tool_name_norm,
                "decision": out.decision.value,
                "reason": out.reason,
                "risk_flags": list(risk_flags),
                "idempotency_key": idempotency_key,
                "ctx": resolved_ctx.model_dump(),
                "meta": meta_norm,
                "confirmed_token_legacy": confirmed_token_legacy,
            }
        )
        return out

    out = ToolGateResponse(
        decision=GateDecision.ALLOW,
        reason=lint_reason,
        risk_flags=risk_flags,
        confirm_prompt=None,
        resume={"token": None, "idempotency_key": idempotency_key},
    )
    _emit_audit(
        {
            "event": "propose",
            "tool": tool_name_norm,
            "decision": out.decision.value,
            "reason": out.reason,
            "risk_flags": list(risk_flags),
            "idempotency_key": idempotency_key,
            "ctx": resolved_ctx.model_dump(),
            "meta": meta_norm,
            "confirmed_token_legacy": confirmed_token_legacy,
        }
    )
    return out


async def apropose(
    tool_name: str,
    args: dict[str, Any] | None = None,
    ctx: GateContext | dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    run_context: dict[str, Any] | None = None,
    policy: dict[str, Any] | GatePolicy | None = None,
) -> ToolGateResponse:
    return await asyncio.to_thread(
        propose,
        tool_name,
        args,
        ctx,
        meta,
        run_context,
        policy,
    )


async def aconfirm(token: str, user_ok: bool = True) -> ConfirmResponse:
    return await asyncio.to_thread(confirm, token, user_ok)
