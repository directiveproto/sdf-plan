from __future__ import annotations

from typing import Dict

from sdf_plan.policy.gate_policy import GatePolicy
from sdf_plan.policy.tool_risk_map import load_default_tool_risk_map


DEFAULT_GATE_POLICY = GatePolicy()
DEFAULT_TOOL_RISK_MAP = load_default_tool_risk_map()


def default_policy() -> GatePolicy:
    return GatePolicy.model_validate(DEFAULT_GATE_POLICY.model_dump())


def default_tool_risk_map() -> Dict[str, dict]:
    # Return a deep-copied plain dict for safe caller mutation.
    return {k: {"category": v["category"], "risk_flags": list(v["risk_flags"])} for k, v in DEFAULT_TOOL_RISK_MAP.items()}
