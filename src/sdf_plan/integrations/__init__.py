"""Legacy decomposition-client integrations.

These integrations are kept for backward compatibility. New runtime gating
integrations should use `sdf_plan.adapters.*` and ToolGate.
"""

from sdf_plan.integrations.crewai import SDFTool
from sdf_plan.integrations.langgraph import sdf_node

__all__ = ["SDFTool", "sdf_node"]
