from importlib.metadata import PackageNotFoundError, version

from sdf_plan.client import decompose_via_api
from sdf_plan.compat import SUPPORTED_SCHEMA_HASHES, assert_schema_compat, package_version
from sdf_plan.lint import LINT_RULES_EVALUATED, lint_plan
from sdf_plan.models import PlanSpecEnvelope, PlanStep
from sdf_plan.policy import policy_annotate
from sdf_plan.preflight import LintError, preflight_lint

try:
    __version__ = version("sdf-plan")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "LINT_RULES_EVALUATED",
    "LintError",
    "PlanSpecEnvelope",
    "PlanStep",
    "SUPPORTED_SCHEMA_HASHES",
    "assert_schema_compat",
    "package_version",
    "decompose_via_api",
    "lint_plan",
    "policy_annotate",
    "preflight_lint",
    "__version__",
]
