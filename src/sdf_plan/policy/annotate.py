from __future__ import annotations

from typing import Any, Dict, List, Tuple

from sdf_plan._internal.policy_helpers import looks_like_write_intent


def policy_annotate(plan: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    steps: List[Dict[str, Any]] = plan.get("steps", []) or []
    confirm_required = 0
    risk_flags_count = 0

    for step in steps:
        intent = (step.get("intent") or "").lower()
        is_write = step.get("type") == "ACT" and looks_like_write_intent(intent)

        risk_flags: List[str] = []
        if is_write:
            risk_flags.append("external_write")

        policy = {
            "requires_confirm": bool(is_write),
            "confirm_prompt": "Confirm before executing side-effecting action" if is_write else None,
            "risk_flags": risk_flags,
        }
        step["policy"] = policy

        if is_write and not step.get("confirm"):
            step["confirm"] = policy["confirm_prompt"]

        step["stop"] = {"kind": "string", "hint": step.get("stop_condition"), "expr": None}
        step["io"] = {
            "inputs": [{"key": str(k), "schema": None} for k in (step.get("inputs") or [])],
            "outputs": [{"key": str(k), "schema": None} for k in (step.get("outputs") or [])],
        }

        if policy["requires_confirm"]:
            confirm_required += 1
        risk_flags_count += len(risk_flags)

    summary = {
        "risk_flags_count": risk_flags_count,
        "confirm_required_steps_count": confirm_required,
    }
    return plan, summary
