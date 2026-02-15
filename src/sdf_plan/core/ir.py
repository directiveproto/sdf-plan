from __future__ import annotations

import warnings
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from sdf_plan.models import PlanSpecEnvelope

class IRAction(BaseModel):
    id: str
    kind: str = "tool_call"
    tool_name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    source: str = "unknown"


class IRSequence(BaseModel):
    version: str = "sdf.ir.v1"
    actions: List[IRAction] = Field(default_factory=list)


def toolcalls_to_ir(tool_calls: List[Dict[str, Any]], *, source: str) -> IRSequence:
    actions: List[IRAction] = []
    for idx, call in enumerate(tool_calls, start=1):
        actions.append(
            IRAction(
                id=str(call.get("id") or f"A{idx}"),
                tool_name=str(call.get("tool_name") or "unknown.tool"),
                args=dict(call.get("args") or {}),
                meta=dict(call.get("meta") or {}),
                source=source,
            )
        )
    return IRSequence(actions=actions)


def planspec_to_ir(plan: PlanSpecEnvelope | Dict[str, Any]) -> IRSequence:
    if isinstance(plan, PlanSpecEnvelope):
        raw = plan.model_dump(by_alias=True)
    elif isinstance(plan, dict):
        raw = dict(plan)
    else:
        raise ValueError("plan must be PlanSpecEnvelope or dict")

    steps = raw.get("steps") or []
    if not isinstance(steps, list):
        raise ValueError("planspec missing steps[]")

    actions: List[IRAction] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError("planspec step must be object")
        step_type = str(step.get("type") or "STEP")
        intent = str(step.get("intent") or "").strip()
        tool_name = str(step.get("tool_name") or _tool_name_from_step_type_and_intent(step_type, intent))
        action = IRAction(
            id=str(step.get("id") or f"S{idx}"),
            kind="tool_call",
            tool_name=tool_name,
            args={
                "inputs": list(step.get("inputs") or []),
                "outputs": list(step.get("outputs") or []),
            },
            meta={
                "source": "planspec",
                "step_type": step.get("type"),
                "title": step.get("title"),
                "intent": step.get("intent"),
                "depends_on": list(step.get("depends_on") or []),
                "stop_condition": step.get("stop_condition"),
                "fallback": step.get("fallback"),
                "retry": step.get("retry"),
                "time_budget_sec": step.get("time_budget_sec"),
                "confirm": step.get("confirm"),
                "idempotency_key": step.get("idempotency_key"),
                "policy": step.get("policy"),
                "stop": step.get("stop"),
                "io": step.get("io"),
            },
            source="planspec",
        )
        actions.append(action)
    return IRSequence(actions=actions)


def ir_to_planspec(
    ir: IRSequence | Dict[str, Any],
    *,
    plan_id: str = "ir-plan",
    template_key: str = "ir",
    confidence: float = 0.5,
    mode_used: str = "deterministic",
) -> PlanSpecEnvelope:
    if isinstance(ir, IRSequence):
        seq = ir
    elif isinstance(ir, dict):
        seq = IRSequence.model_validate(ir)
    else:
        raise ValueError("ir must be IRSequence or dict")

    steps: List[Dict[str, Any]] = []
    for idx, action in enumerate(seq.actions, start=1):
        if action.kind != "tool_call":
            warnings.warn(
                f"Non-lossless mapping: unsupported IR action kind '{action.kind}' on action {action.id}; coercing to ACT.",
                UserWarning,
            )

        args = dict(action.args or {})
        meta = dict(action.meta or {})

        mapped_inputs = _as_list_of_str(args.get("inputs"))
        mapped_outputs = _as_list_of_str(args.get("outputs"))

        dropped_args = sorted(k for k in args.keys() if k not in {"inputs", "outputs"})
        if dropped_args:
            warnings.warn(
                f"Non-lossless mapping: dropped IR args keys for action {action.id}: {dropped_args}",
                UserWarning,
            )

        known_meta_keys = {
            "source",
            "step_type",
            "title",
            "intent",
            "depends_on",
            "stop_condition",
            "fallback",
            "retry",
            "time_budget_sec",
            "confirm",
            "idempotency_key",
            "policy",
            "stop",
            "io",
        }
        dropped_meta = sorted(k for k in meta.keys() if k not in known_meta_keys)
        if dropped_meta:
            warnings.warn(
                f"Non-lossless mapping: dropped IR meta keys for action {action.id}: {dropped_meta}",
                UserWarning,
            )

        step_id = str(action.id or f"S{idx}")
        step_type = str(meta.get("step_type") or "ACT")
        title = str(meta.get("title") or action.tool_name)
        intent = str(meta.get("intent") or action.tool_name)
        depends_on = _as_list_of_str(meta.get("depends_on"))
        stop_condition = str(meta.get("stop_condition") or f"Step {step_id} completed")
        fallback = str(meta.get("fallback") or "manual_review")
        retry = int(meta.get("retry") or 0)
        time_budget_sec = int(meta.get("time_budget_sec") or 0)
        confirm = meta.get("confirm")
        if confirm is not None:
            confirm = str(confirm)

        policy = meta.get("policy")
        stop = meta.get("stop")
        io = meta.get("io")
        if io is None:
            io = {
                "inputs": [{"key": i, "schema": None} for i in mapped_inputs],
                "outputs": [{"key": o, "schema": None} for o in mapped_outputs],
            }
        if stop is None:
            stop = {"kind": "string", "hint": stop_condition, "expr": None}

        step = {
            "id": step_id,
            "type": step_type,
            "title": title,
            "intent": intent,
            "inputs": mapped_inputs,
            "outputs": mapped_outputs,
            "depends_on": depends_on,
            "stop_condition": stop_condition,
            "fallback": fallback,
            "retry": retry,
            "time_budget_sec": time_budget_sec,
            "confirm": confirm,
            "idempotency_key": meta.get("idempotency_key"),
            "policy": policy,
            "stop": stop,
            "io": io,
        }
        steps.append(step)

    return PlanSpecEnvelope(
        plan_id=plan_id,
        template_key=template_key,
        confidence=confidence,
        mode_used=mode_used,
        steps=steps,
    )


def _as_list_of_str(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _tool_name_from_step_type_and_intent(step_type: str, intent: str) -> str:
    t = step_type.strip().upper()
    if t == "ACT":
        i = intent.strip().lower()
        if i:
            return i.replace(" ", "_")
        return "act.unknown"
    return f"planspec.{t.lower()}"
