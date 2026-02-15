from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

from sdf_plan.core.hashing import hash_canonical
from sdf_plan.gate.contracts import (
    ConfirmResponse,
    GateDecision,
    GateErrorCode,
    ToolGateResponse,
)
from sdf_plan.gate.idempotency import generate_idempotency_key
from sdf_plan.lint import lint_tool_mode
from sdf_plan.policy import GatePolicy, VerifyBeforeWriteMode, classify_tool, load_tool_risk_map

_DEFAULT_TOKEN_TTL_SEC = 600
_DEFAULT_SECRET = "sdf-plan-dev-secret"


def _secret() -> bytes:
    return os.getenv("SDF_PLAN_TOKEN_SECRET", _DEFAULT_SECRET).encode("utf-8")


def _now() -> int:
    return int(time.time())


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def _sign_payload(payload: dict[str, Any]) -> str:
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64url(payload_json)
    sig = hmac.new(_secret(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    sig_b64 = _b64url(sig)
    return f"{payload_b64}.{sig_b64}"


def _verify_token(token: str) -> dict[str, Any]:
    parts = (token or "").split(".")
    if len(parts) != 2:
        raise ValueError("INVALID_TOKEN")

    payload_b64, sig_b64 = parts
    expected_sig = hmac.new(_secret(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url(expected_sig), sig_b64):
        raise ValueError("TOKEN_TAMPERED")

    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise ValueError("INVALID_TOKEN") from exc

    exp = int(payload.get("exp", 0))
    if _now() > exp:
        raise ValueError("TOKEN_EXPIRED")

    return payload


def _to_policy(policy: dict[str, Any] | GatePolicy | None) -> GatePolicy:
    if policy is None:
        return GatePolicy()
    if isinstance(policy, GatePolicy):
        return policy
    return GatePolicy.model_validate(policy)


def _is_write_tool(category: str, risk_flags: list[str]) -> bool:
    if category.startswith("write"):
        return True
    write_like = {"write", "external_side_effect", "payment", "prod_change", "credential_access"}
    return any(flag in write_like for flag in risk_flags)


def _has_verify_context(run_context: dict[str, Any] | None) -> bool:
    ctx = run_context or {}
    if ctx.get("verified") is True:
        return True

    actions = ctx.get("recent_actions") or []
    for action in actions:
        if not isinstance(action, dict):
            continue
        kind = str(action.get("kind") or "").lower()
        tool_name = str(action.get("tool_name") or "").lower()
        if kind in {"verify", "confirm"}:
            return True
        if "verify" in tool_name or tool_name.endswith(".read"):
            return True
    return False


def _issue_resume_token(*, tool_name: str, args_hash: str, scope: Any, idempotency_key: str | None, ttl_sec: int = _DEFAULT_TOKEN_TTL_SEC) -> str:
    payload = {
        "tool": tool_name,
        "args_hash": args_hash,
        "scope": scope,
        "idempotency_key": idempotency_key,
        "iat": _now(),
        "exp": _now() + int(ttl_sec),
    }
    return _sign_payload(payload)


def confirm(token: str, user_ok: bool = True) -> ConfirmResponse:
    if not user_ok:
        return ConfirmResponse(
            decision=GateDecision.BLOCK,
            confirmed=False,
            error_code=GateErrorCode.POLICY_BLOCKED,
            reason="User denied confirmation",
        )

    try:
        payload = _verify_token(token)
    except ValueError as exc:
        code = str(exc)
        if code == "TOKEN_EXPIRED":
            err = GateErrorCode.TOKEN_EXPIRED
        elif code == "TOKEN_TAMPERED":
            err = GateErrorCode.TOKEN_TAMPERED
        else:
            err = GateErrorCode.INVALID_TOKEN
        return ConfirmResponse(
            decision=GateDecision.BLOCK,
            confirmed=False,
            error_code=err,
            reason=code,
        )

    return ConfirmResponse(
        decision=GateDecision.ALLOW,
        confirmed=True,
        reason="CONFIRMED",
        idempotency_key=payload.get("idempotency_key"),
    )


def propose(
    tool_name: str,
    args: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    policy: dict[str, Any] | GatePolicy | None = None,
    run_context: dict[str, Any] | None = None,
) -> ToolGateResponse:
    tool_name_norm = (tool_name or "").strip().lower()
    args_norm = dict(args or {})
    meta_norm = dict(meta or {})
    run_ctx = dict(run_context or {})

    # 1) normalize / classify
    gp = _to_policy(policy)
    risk_map_overrides = None
    if isinstance(policy, dict):
        risk_map_overrides = policy.get("tool_risk_map_overrides")
    risk_map = load_tool_risk_map(risk_map_overrides)
    classification = classify_tool(tool_name_norm, risk_map)
    risk_flags = list(classification.risk_flags)
    is_write = _is_write_tool(classification.category, risk_flags)
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
    if is_write and gp.verify_before_write != VerifyBeforeWriteMode.OFF:
        has_verify = _has_verify_context(run_ctx)
        if not has_verify:
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
        c = confirm(str(confirmed_token), user_ok=True)
        if c.confirmed:
            args_h = hash_canonical(args_norm)
            expected_scope = run_ctx.get("workspace_id") or meta_norm.get("workspace_id")
            try:
                payload = _verify_token(str(confirmed_token))
            except ValueError:
                payload = None
            if payload and payload.get("tool") == tool_name_norm and payload.get("args_hash") == args_h and payload.get("scope") == expected_scope:
                requires_confirm = False
                policy_block = False
                verify_warning = False
                verify_block = False

    # 4) idempotency checks
    idempotency_key = None
    if is_write and gp.require_idempotency_for_write:
        scope = run_ctx.get("workspace_id") or meta_norm.get("workspace_id") or "global"
        exclude_fields = meta_norm.get("idempotency_exclude_fields") or []
        idempotency_key = generate_idempotency_key(
            scope=scope,
            tool_name=tool_name_norm,
            args=args_norm,
            exclude_fields=exclude_fields,
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
        return ToolGateResponse(
            decision=GateDecision.BLOCK,
            reason=reason,
            error_code=GateErrorCode.POLICY_BLOCKED,
            risk_flags=risk_flags,
            confirm_prompt=None,
            resume=None,
        )

    if requires_confirm:
        args_h = hash_canonical(args_norm)
        scope = run_ctx.get("workspace_id") or meta_norm.get("workspace_id")
        token = _issue_resume_token(
            tool_name=tool_name_norm,
            args_hash=args_h,
            scope=scope,
            idempotency_key=idempotency_key,
        )
        prompt = meta_norm.get("confirm_prompt") or "Confirm before executing side-effecting action"
        return ToolGateResponse(
            decision=GateDecision.BLOCK,
            reason="WRITE_REQUIRES_CONFIRM" if is_write else (lint_reason or "REQUIRES_CONFIRM"),
            error_code=GateErrorCode.POLICY_BLOCKED,
            risk_flags=risk_flags,
            confirm_prompt=str(prompt),
            resume={"token": token, "idempotency_key": idempotency_key},
        )

    if verify_warning:
        return ToolGateResponse(
            decision=GateDecision.WARN,
            reason="NO_VERIFY_BEFORE_WRITE",
            risk_flags=risk_flags,
            confirm_prompt=None,
            resume={"token": None, "idempotency_key": idempotency_key},
        )

    return ToolGateResponse(
        decision=GateDecision.ALLOW,
        reason=lint_reason,
        risk_flags=risk_flags,
        confirm_prompt=None,
        resume={"token": None, "idempotency_key": idempotency_key},
    )
