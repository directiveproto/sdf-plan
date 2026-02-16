from __future__ import annotations

from typing import Any, Dict, List

from sdf_plan._internal.policy_helpers import has_verify_context, is_write_tool
from sdf_plan.gate.contracts import GateDecision
from sdf_plan.policy import GatePolicy, VerifyBeforeWriteMode, classify_tool, load_tool_risk_map


def _warn(code: str, msg: str) -> Dict[str, Any]:
    return {"level": "WARN", "code": code, "message": msg, "step_id": None}


def _error(code: str, msg: str) -> Dict[str, Any]:
    return {"level": "ERROR", "code": code, "message": msg, "step_id": None}


def _to_policy(policy: dict[str, Any] | GatePolicy | None) -> GatePolicy:
    if policy is None:
        return GatePolicy()
    if isinstance(policy, GatePolicy):
        return policy
    return GatePolicy.model_validate(policy)


def lint_tool_mode(
    *,
    tool_name: str,
    args: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    policy: dict[str, Any] | GatePolicy | None = None,
    run_context: dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    _ = dict(args or {})
    meta_norm = dict(meta or {})
    gp = _to_policy(policy)

    risk_overrides = None
    if isinstance(policy, dict):
        risk_overrides = policy.get("tool_risk_map_overrides")
    risk_map = load_tool_risk_map(risk_overrides)

    cls = classify_tool((tool_name or "").strip().lower(), risk_map)
    findings: List[Dict[str, Any]] = []
    is_write = is_write_tool(cls.category, cls.risk_flags)

    if cls.category == "unknown":
        if gp.unknown_tool == GateDecision.BLOCK or gp.strict_mode:
            findings.append(_error("UNKNOWN_TOOL", "Unknown tool is blocked by policy"))
        else:
            findings.append(_warn("UNKNOWN_TOOL", "Unknown tool requires confirmation by default policy"))

    if is_write and gp.write_requires_confirm and not meta_norm.get("confirmed_token"):
        findings.append(_error("WRITE_REQUIRES_CONFIRM", "Write tool requires confirmation"))

    explicit_idem = meta_norm.get("idempotency_key")
    auto_idem_disabled = bool(meta_norm.get("disable_auto_idempotency", False))
    if is_write and gp.require_idempotency_for_write and not explicit_idem and auto_idem_disabled:
        findings.append(_error("ACT_WITHOUT_IDEMPOTENCY", "Write tool missing idempotency key while auto-idempotency is disabled"))

    if is_write and run_context is not None and gp.verify_before_write != VerifyBeforeWriteMode.OFF:
        if not has_verify_context(run_context):
            if gp.verify_before_write == VerifyBeforeWriteMode.ENFORCE:
                findings.append(_error("NO_VERIFY_BEFORE_WRITE", "No verify/read context found before write tool call"))
            else:
                findings.append(_warn("NO_VERIFY_BEFORE_WRITE", "No verify/read context found before write tool call"))

    return findings
