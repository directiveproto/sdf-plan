from __future__ import annotations

from typing import Any, Dict, List

from sdf_plan.models import PlanSpecEnvelope


def _tool_name_from_step(step: Dict[str, Any]) -> str:
    if step.get("tool_name"):
        return str(step["tool_name"])
    step_type = str(step.get("type") or "STEP").strip().upper()
    if step_type == "ACT":
        intent = str(step.get("intent") or "").strip().lower()
        return intent.replace(" ", "_") if intent else "act.unknown"
    return f"planspec.{step_type.lower()}"


def parse_planspec(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, PlanSpecEnvelope):
        plan = payload.model_dump(by_alias=True)
    elif isinstance(payload, dict):
        plan = payload
    else:
        raise ValueError("planspec payload must be dict or PlanSpecEnvelope")

    steps = plan.get("steps")
    if not isinstance(steps, list):
        raise ValueError("planspec payload missing steps[]")

    out: List[Dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError("planspec step must be object")
        out.append(
            {
                "id": str(step.get("id") or f"S{idx}"),
                "tool_name": _tool_name_from_step(step),
                "args": {
                    "inputs": list(step.get("inputs") or []),
                    "outputs": list(step.get("outputs") or []),
                },
                "meta": {
                    "source": "planspec",
                    "step_type": step.get("type"),
                    "title": step.get("title"),
                    "intent": step.get("intent"),
                    "depends_on": list(step.get("depends_on") or []),
                },
            }
        )

    return out
