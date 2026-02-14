from __future__ import annotations

from typing import Any, Dict, Optional

from sdf_plan.client import decompose_via_api
from sdf_plan.preflight import preflight_lint


class SDFTool:
    """CrewAI-friendly adapter (works as a plain callable tool class)."""

    name = "sdf_plan_tool"
    description = "Generate and lint a bounded plan using SDF Cloud."

    def __init__(
        self,
        *,
        api_base: str,
        api_key: str,
        default_max_steps: int = 12,
        default_safety_mode: str = "safe",
    ):
        self.api_base = api_base
        self.api_key = api_key
        self.default_max_steps = default_max_steps
        self.default_safety_mode = default_safety_mode

    def run(
        self,
        goal: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[list[dict]] = None,
        mode: str = "deterministic",
        max_steps: Optional[int] = None,
        safety_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        plan = decompose_via_api(
            api_base=self.api_base,
            api_key=self.api_key,
            goal=goal,
            context=context or {},
            tools=tools or [],
            mode=mode,
            max_steps=max_steps or self.default_max_steps,
            safety_mode=safety_mode or self.default_safety_mode,
        )
        preflight_lint(
            plan,
            max_steps=max_steps or self.default_max_steps,
            safety_mode=safety_mode or self.default_safety_mode,
        )
        return plan
