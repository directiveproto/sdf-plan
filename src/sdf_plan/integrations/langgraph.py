from __future__ import annotations

from typing import Any, Dict

from sdf_plan.client import decompose_via_api
from sdf_plan.preflight import preflight_lint


def sdf_node(
    *,
    api_base: str,
    api_key: str,
    default_max_steps: int = 12,
    default_safety_mode: str = "safe",
    output_key: str = "sdf_plan",
) -> Any:
    """Return a LangGraph-compatible node callable.

    Input state expects:
    - goal: str (required)
    - context: dict (optional)
    - tools: list (optional)
    - mode: str (optional)
    - options.max_steps / options.safety_mode (optional)
    """

    def node(state: Dict[str, Any]) -> Dict[str, Any]:
        goal = state.get("goal")
        if not goal:
            raise ValueError("state.goal is required for sdf_node")

        options = state.get("options") or {}
        plan = decompose_via_api(
            api_base=api_base,
            api_key=api_key,
            goal=goal,
            context=state.get("context") or {},
            tools=state.get("tools") or [],
            mode=state.get("mode") or "deterministic",
            max_steps=int(options.get("max_steps", default_max_steps)),
            safety_mode=str(options.get("safety_mode", default_safety_mode)),
        )
        preflight_lint(plan, max_steps=int(options.get("max_steps", default_max_steps)), safety_mode=str(options.get("safety_mode", default_safety_mode)))
        return {output_key: plan}

    return node
