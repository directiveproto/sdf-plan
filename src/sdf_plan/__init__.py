from importlib.metadata import PackageNotFoundError, version

from sdf_plan.client import decompose_via_api
from sdf_plan.compat import SUPPORTED_SCHEMA_HASHES, assert_schema_compat, package_version
from sdf_plan.config import SdfPlanConfig, configure
from sdf_plan.core import IRAction, IRSequence, ir_to_planspec, normalize_to_ir, planspec_to_ir, toolcalls_to_ir
from sdf_plan.adapters import crewai_tool_gate, langchain_tool_gate, langgraph_tool_gate_node
from sdf_plan.gate.contracts import (
    ConfirmRequest,
    ConfirmResponse,
    GateContext,
    GateDecision,
    GateErrorCode,
    ToolGateRequest,
    ToolGateResponse,
)
from sdf_plan.gate.tool_gate import aconfirm, apropose, confirm, propose
from sdf_plan.lint import LINT_RULES_EVALUATED, lint_plan
from sdf_plan.models import PlanSpecEnvelope, PlanStep
from sdf_plan.policy import policy_annotate
from sdf_plan.preflight import LintError, preflight_lint

try:
    __version__ = version("sdf-plan")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "ConfirmRequest",
    "ConfirmResponse",
    "GateContext",
    "GateDecision",
    "GateErrorCode",
    "IRAction",
    "IRSequence",
    "LINT_RULES_EVALUATED",
    "LintError",
    "PlanSpecEnvelope",
    "PlanStep",
    "SUPPORTED_SCHEMA_HASHES",
    "ToolGateRequest",
    "ToolGateResponse",
    "assert_schema_compat",
    "aconfirm",
    "apropose",
    "confirm",
    "configure",
    "package_version",
    "propose",
    "SdfPlanConfig",
    "decompose_via_api",
    "langgraph_tool_gate_node",
    "lint_plan",
    "crewai_tool_gate",
    "langchain_tool_gate",
    "ir_to_planspec",
    "normalize_to_ir",
    "planspec_to_ir",
    "policy_annotate",
    "preflight_lint",
    "toolcalls_to_ir",
    "__version__",
]
